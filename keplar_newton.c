/*
 * keplar_newton.c - Demonstrates Kepler's three laws of planetary motion.
 *
 *   1st law: Planets move in ellipses with the Sun at one focus.
 *   2nd law: A line from the Sun to a planet sweeps out equal areas
 *            in equal times.
 *   3rd law: The square of the orbital period is proportional to the
 *            cube of the semi-major axis (T^2 = a^3 in years and AU).
 *
 * The final section integrates Newton's law of gravity step by step,
 * without using any of Kepler's formulas, and measures the resulting
 * orbits to show that all three laws emerge from the inverse-square force.
 *
 * Build: cc -std=c99 -Wall -Wextra -pedantic -O2 keplar_newton.c -o keplar_newton -lm
 */

#include <math.h>
#include <stdio.h>

#define PI 3.14159265358979323846

typedef struct {
    const char *name;
    double a;          /* semi-major axis (AU) */
    double e;          /* eccentricity */
    double period_obs; /* observed sidereal period (years) */
} Planet;

static const Planet planets[] = {
    {"Mercury",  0.387098, 0.205630,   0.240846},
    {"Venus",    0.723332, 0.006772,   0.615198},
    {"Earth",    1.000000, 0.016710,   1.000017},
    {"Mars",     1.523679, 0.093400,   1.880850},
    {"Jupiter",  5.2044,   0.048900,  11.862000},
    {"Saturn",   9.5826,   0.056500,  29.457100},
    {"Uranus",  19.2184,   0.046380,  84.020500},
    {"Neptune", 30.1100,   0.009456, 164.800000},
};

enum { NUM_PLANETS = sizeof planets / sizeof planets[0] };

/* Solve Kepler's equation M = E - e*sin(E) for E using Newton's method. */
static double eccentric_anomaly(double M, double e)
{
    double E = (e < 0.8) ? M : PI;
    for (int i = 0; i < 50; i++) {
        double delta = (E - e * sin(E) - M) / (1.0 - e * cos(E));
        E -= delta;
        if (fabs(delta) < 1e-14)
            break;
    }
    return E;
}

/* Position of a planet at fraction t (0..1) of its orbit, starting at
 * perihelion. Returns heliocentric distance r (AU) and true anomaly nu. */
static void orbital_position(const Planet *p, double t, double *r, double *nu)
{
    double M = 2.0 * PI * t;
    double E = eccentric_anomaly(M, p->e);
    *nu = 2.0 * atan2(sqrt(1.0 + p->e) * sin(E / 2.0),
                      sqrt(1.0 - p->e) * cos(E / 2.0));
    *r = p->a * (1.0 - p->e * cos(E));
}

static void first_law(void)
{
    puts("=== Kepler's 1st Law: orbits are ellipses with the Sun at a focus ===\n");
    printf("%-8s %10s %10s %12s %12s %10s\n",
           "Planet", "a (AU)", "b (AU)", "Perihelion", "Aphelion", "Focus c");
    for (int i = 0; i < NUM_PLANETS; i++) {
        const Planet *p = &planets[i];
        double b = p->a * sqrt(1.0 - p->e * p->e);
        double c = p->a * p->e;
        printf("%-8s %10.4f %10.4f %12.4f %12.4f %10.4f\n",
               p->name, p->a, b, p->a * (1.0 - p->e), p->a * (1.0 + p->e), c);
    }

    /* Verify the ellipse equation r = a(1-e^2)/(1+e cos nu) for Mercury. */
    const Planet *m = &planets[0];
    double max_err = 0.0;
    for (int k = 0; k < 360; k++) {
        double r, nu;
        orbital_position(m, k / 360.0, &r, &nu);
        double r_ellipse = m->a * (1.0 - m->e * m->e) / (1.0 + m->e * cos(nu));
        double err = fabs(r - r_ellipse);
        if (err > max_err)
            max_err = err;
    }
    printf("\nCheck: %s's computed positions match the focal ellipse equation\n"
           "       r = a(1-e^2)/(1+e cos v) to within %.2e AU.\n\n",
           m->name, max_err);
}

/* Area swept between fractions t0 and t1 of the orbit, by integrating
 * dA = r^2/2 dnu numerically. */
static double swept_area(const Planet *p, double t0, double t1)
{
    const int steps = 10000;
    double area = 0.0, r_prev, nu_prev;
    orbital_position(p, t0, &r_prev, &nu_prev);
    for (int i = 1; i <= steps; i++) {
        double r, nu;
        orbital_position(p, t0 + (t1 - t0) * i / steps, &r, &nu);
        double dnu = nu - nu_prev;
        if (dnu < -PI) dnu += 2.0 * PI; /* handle wrap-around at +/-pi */
        area += 0.5 * r * r_prev * sin(dnu); /* triangle area */
        r_prev = r;
        nu_prev = nu;
    }
    return area;
}

static void second_law(void)
{
    const Planet *p = &planets[0]; /* Mercury: most eccentric, clearest demo */
    const int segments = 12;
    double b = p->a * sqrt(1.0 - p->e * p->e);
    double expected = PI * p->a * b / segments;

    puts("=== Kepler's 2nd Law: equal areas in equal times ===\n");
    printf("%s's orbit split into %d equal time intervals (%.2f days each):\n\n",
           p->name, segments, p->period_obs * 365.25 / segments);
    printf("%-8s %12s %12s %14s\n", "Segment", "r start", "Speed", "Area (AU^2)");
    for (int s = 0; s < segments; s++) {
        double t0 = (double)s / segments;
        double t1 = (double)(s + 1) / segments;
        double r, nu;
        orbital_position(p, t0, &r, &nu);
        /* vis-viva, in AU/yr with GM_sun = 4 pi^2 AU^3/yr^2 */
        double v = sqrt(4.0 * PI * PI * (2.0 / r - 1.0 / p->a));
        printf("%-8d %9.4f AU %6.2f AU/yr %14.6f\n",
               s + 1, r, v, swept_area(p, t0, t1));
    }
    printf("\nExpected area per interval (pi*a*b / %d): %.6f AU^2\n", segments, expected);
    puts("The planet moves faster near perihelion, yet every interval sweeps the same area.\n");
}

static void third_law(void)
{
    puts("=== Kepler's 3rd Law: T^2 = a^3 (T in years, a in AU) ===\n");
    printf("%-8s %10s %14s %14s %10s %10s\n",
           "Planet", "a (AU)", "T predicted", "T observed", "Error %", "T^2/a^3");
    for (int i = 0; i < NUM_PLANETS; i++) {
        const Planet *p = &planets[i];
        double T = pow(p->a, 1.5);
        double err = 100.0 * (T - p->period_obs) / p->period_obs;
        double ratio = p->period_obs * p->period_obs / (p->a * p->a * p->a);
        printf("%-8s %10.4f %11.4f yr %11.4f yr %+9.3f%% %10.4f\n",
               p->name, p->a, T, p->period_obs, err, ratio);
    }
    puts("\nT^2/a^3 is ~1 for every planet, as Kepler's 3rd law predicts.");
}

/* ------------------------------------------------------------------------
 * Newtonian gravity simulation
 *
 * Units: AU and years, in which G*M_sun = 4*pi^2. The planet's mass is
 * neglected. Nothing below assumes an ellipse: the orbit is found by
 * repeatedly applying a = -GM r / |r|^3, then measured.
 * ------------------------------------------------------------------------ */

#define GM (4.0 * PI * PI)

typedef struct {
    double x, y, vx, vy;
} State;

typedef struct {
    double r_min, r_max;   /* measured perihelion / aphelion distances */
    double a, e;           /* derived from r_min and r_max */
    double period;         /* time to sweep 360 degrees around the Sun */
    double apse_skew;      /* |angle(aphelion) - angle(perihelion)| - pi */
    double ellipse_err;    /* max |r(1 + e cos(v)) - a(1 - e^2)| / a */
    double area_rate_var;  /* (max - min) / mean of dA/dt */
    long steps;            /* integration steps per orbit */
} SimResult;

static void gravity(double x, double y, double *ax, double *ay)
{
    double r = hypot(x, y);
    double k = -GM / (r * r * r);
    *ax = k * x;
    *ay = k * y;
}

/* One kick-drift-kick leapfrog step (symplectic, so energy does not drift). */
static void leapfrog_step(State *s, double dt)
{
    double ax, ay;
    gravity(s->x, s->y, &ax, &ay);
    s->vx += 0.5 * dt * ax;
    s->vy += 0.5 * dt * ay;
    s->x += dt * s->vx;
    s->y += dt * s->vy;
    gravity(s->x, s->y, &ax, &ay);
    s->vx += 0.5 * dt * ax;
    s->vy += 0.5 * dt * ay;
}

/* Fit a parabola through three equally spaced samples (y0, y1, y2) and
 * return the vertex value; the matching angle is interpolated too. */
static void refine_extremum(const double y[3], const double th[3],
                            double *y_ext, double *th_ext)
{
    double d = y[0] - 2.0 * y[1] + y[2];
    double s = (d != 0.0) ? 0.5 * (y[0] - y[2]) / d : 0.0;
    *y_ext = y[1] - 0.25 * (y[0] - y[2]) * s;
    *th_ext = th[1] + 0.5 * s * (th[2] - th[0]);
}

static double wrap_angle(double a)
{
    while (a > PI) a -= 2.0 * PI;
    while (a <= -PI) a += 2.0 * PI;
    return a;
}

static void simulate_orbit(State init, SimResult *res)
{
    /* Step size from the starting dynamical timescale r/v only. */
    double dt = 1e-4 * hypot(init.x, init.y) / hypot(init.vx, init.vy);

    /* Pass 1: integrate until the planet has gone once around and both
     * apsides have been seen; record distances, angles and dA/dt. */
    State s = init;
    double r[3], th[3];     /* samples n-2, n-1, n */
    double swept = 0.0;     /* unwrapped angle travelled */
    double th_min = 0.0, th_max = 0.0;
    int have_min = 0, have_max = 0;
    double h_min = HUGE_VAL, h_max = -HUGE_VAL, h_sum = 0.0;
    long n = 0;

    r[2] = hypot(s.x, s.y);
    th[2] = atan2(s.y, s.x);
    res->period = 0.0;

    while (!(res->period > 0.0 && have_min && have_max) && n < 100000000L) {
        leapfrog_step(&s, dt);
        n++;

        /* dA/dt = |r x v| / 2 */
        double h = 0.5 * fabs(s.x * s.vy - s.y * s.vx);
        if (h < h_min) h_min = h;
        if (h > h_max) h_max = h;
        h_sum += h;

        double prev_swept = swept;
        double th_new = th[2] + wrap_angle(atan2(s.y, s.x) - th[2]);
        swept += th_new - th[2];
        r[0] = r[1]; r[1] = r[2]; r[2] = hypot(s.x, s.y);
        th[0] = th[1]; th[1] = th[2]; th[2] = th_new;

        if (res->period == 0.0 && swept >= 2.0 * PI)
            res->period = dt * ((n - 1) + (2.0 * PI - prev_swept) / (swept - prev_swept));

        if (n >= 2) {
            if (!have_min && r[1] < r[0] && r[1] <= r[2]) {
                refine_extremum(r, th, &res->r_min, &th_min);
                have_min = 1;
            }
            if (!have_max && r[1] > r[0] && r[1] >= r[2]) {
                refine_extremum(r, th, &res->r_max, &th_max);
                have_max = 1;
            }
        }
    }

    res->a = 0.5 * (res->r_min + res->r_max);
    res->e = (res->r_max - res->r_min) / (res->r_max + res->r_min);
    res->apse_skew = fabs(wrap_angle(th_max - th_min)) - PI;
    res->area_rate_var = (h_max - h_min) / (h_sum / n);
    res->steps = (long)ceil(res->period / dt);

    /* Pass 2: replay one orbit and test every point against the focal
     * ellipse built from the measured a, e and perihelion direction. */
    s = init;
    double p = res->a * (1.0 - res->e * res->e);
    res->ellipse_err = 0.0;
    for (long i = 0; i <= res->steps; i++) {
        double rr = hypot(s.x, s.y);
        double nu = atan2(s.y, s.x) - th_min;
        double err = fabs(rr * (1.0 + res->e * cos(nu)) - p) / res->a;
        if (err > res->ellipse_err)
            res->ellipse_err = err;
        leapfrog_step(&s, dt);
    }
}

static void print_sim_row(const char *name, const SimResult *r, double e_ref)
{
    char e_ref_buf[16] = "     -";
    if (e_ref >= 0.0)
        snprintf(e_ref_buf, sizeof e_ref_buf, "%.5f", e_ref);
    printf("%-8s %9.4f %8.5f %8s %11.4f %9.6f %9.1e %9.1e %9.1e\n",
           name, r->a, r->e, e_ref_buf, r->period,
           r->period * r->period / (r->a * r->a * r->a),
           r->ellipse_err, r->apse_skew, r->area_rate_var);
}

static void newton_simulation(void)
{
    puts("\n=== Newtonian gravity simulation: do Kepler's laws emerge? ===\n");
    puts("Each orbit is integrated from F = -GMm r/|r|^3 alone (leapfrog, tens of");
    puts("thousands of steps/orbit). a and e are then *measured* from the");
    puts("closest and farthest distances, and every step is tested against the\nfocal ellipse.\n");
    printf("%-8s %9s %8s %8s %11s %9s %9s %9s %9s\n",
           "Orbit", "a meas", "e meas", "e table", "T sim (yr)", "T^2/a^3",
           "Ellipse", "Apse skew", "dA/dt var");

    for (int i = 0; i < NUM_PLANETS; i++) {
        const Planet *p = &planets[i];
        /* Launch from perihelion distance with the energy-conserving speed
         * for this a (vis-viva) - just an initial condition, not a shape. */
        double r0 = p->a * (1.0 - p->e);
        State init = {r0, 0.0, 0.0, sqrt(GM * (2.0 / r0 - 1.0 / p->a))};
        SimResult res;
        simulate_orbit(init, &res);
        print_sim_row(p->name, &res, p->e);
    }

    /* An arbitrary launch: 1 AU out, thrown at 5.4 AU/yr at an odd angle,
     * with nothing chosen to make an ellipse. */
    State init = {1.0, 0.0, 2.0, 5.0};
    SimResult res;
    simulate_orbit(init, &res);
    print_sim_row("Thrown", &res, -1.0);

    puts("\nEllipse:   worst relative miss of r(1 + e cos v) = a(1 - e^2)  -> 1st law");
    puts("Apse skew: aphelion is directly opposite perihelion (radians) -> 1st law");
    puts("dA/dt var: spread of areal velocity |r x v|/2 over the orbit  -> 2nd law");
    puts("T^2/a^3:   measured period vs measured size, equals 1         -> 3rd law");
    puts("\nThe 2nd law holds to rounding error because gravity is a central force:");
    puts("it never changes r x v, and the leapfrog steps preserve that exactly.");
}

int main(void)
{
    first_law();
    second_law();
    third_law();
    newton_simulation();
    return 0;
}
