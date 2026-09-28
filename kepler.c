/*
 * kepler.c - Demonstrates Kepler's three laws of planetary motion.
 *
 *   1st law: Planets move in ellipses with the Sun at one focus.
 *   2nd law: A line from the Sun to a planet sweeps out equal areas
 *            in equal times.
 *   3rd law: The square of the orbital period is proportional to the
 *            cube of the semi-major axis (T^2 = a^3 in years and AU).
 *
 * Build: cc -std=c99 -Wall -Wextra -pedantic -O2 kepler.c -o kepler -lm
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

int main(void)
{
    first_law();
    second_law();
    third_law();
    return 0;
}
