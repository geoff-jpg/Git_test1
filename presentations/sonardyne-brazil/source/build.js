const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

// Palette: Sonardyne navy / green / gold, tuned for a dark canvas
const C = {
  navy: "0A2540", deep: "061829", card: "0F2F4F", cardHi: "143A60", line: "24507A",
  green: "17B584", greenDk: "0E8A5F", gold: "F2C12E", white: "FFFFFF",
  text: "E8EFF6", muted: "9FB3C8", dim: "6F87A0",
};
const HF = "Arial";   // headings
const BF = "Calibri"; // body
const TOTAL = 12;

async function icon(Comp, color, size = 256) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.title = "Sonardyne in Brazil";
pres.company = "Sonardyne";

function contentSlide(n, kicker, title) {
  const s = pres.addSlide();
  s.background = { path: path.join(__dirname, "bg_content.png") };
  s.addText(kicker.toUpperCase(), { x: 0.5, y: 0.32, w: 7, h: 0.25, fontFace: BF, fontSize: 10, bold: true, color: C.green, charSpacing: 3, margin: 0, isTextBox: true });
  s.addText(title, { x: 0.5, y: 0.55, w: 9, h: 0.6, fontFace: HF, fontSize: 24, bold: true, color: C.white, margin: 0, valign: "top", isTextBox: true });
  s.addText("Sonardyne in Brazil", { x: 0.5, y: 5.2, w: 3, h: 0.22, fontFace: BF, fontSize: 9, color: C.dim, margin: 0, isTextBox: true });
  s.addText(`${String(n).padStart(2, "0")} / ${TOTAL}`, { x: 8.5, y: 5.2, w: 1, h: 0.22, fontFace: BF, fontSize: 9, color: C.dim, align: "right", margin: 0, isTextBox: true });
  return s;
}
function card(s, x, y, w, h, fill = C.card) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: C.line, width: 0.75 } });
}
function iconDot(s, data, x, y, d, fill) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" } });
  const p = d * 0.26;
  s.addImage({ data, x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p });
}

(async () => {
  const I = {};
  const want = { industry: fa.FaIndustry, flask: fa.FaFlask, ship: fa.FaShip, down: fa.FaArrowDown, wifi: fa.FaWifi,
    wave: fa.FaWaveSquare, bulb: fa.FaLightbulb, layers: fa.FaLayerGroup, search: fa.FaSearch, chart: fa.FaChartLine,
    hand: fa.FaHandshake, pin: fa.FaMapMarkerAlt, robot: fa.FaRobot, tower: fa.FaBroadcastTower, cog: fa.FaCogs,
    globe: fa.FaGlobeAmericas, anchor: fa.FaAnchor, crosshair: fa.FaCrosshairs, compass: fa.FaCompass,
    satellite: fa.FaSatelliteDish, rocket: fa.FaRocket, quote: fa.FaQuoteLeft };
  for (const [k, v] of Object.entries(want)) { I[k] = await icon(v, C.white); I[k + "N"] = await icon(v, C.navy); }

  // ---------- 1. Title ----------
  {
    const s = pres.addSlide();
    s.background = { path: path.join(__dirname, "bg_title.png") };
    s.addText("SEPTEMBER 2026 BRIEFING", { x: 0.6, y: 1.25, w: 5, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: C.green, charSpacing: 4, margin: 0, isTextBox: true });
    s.addText("Sonardyne\nin Brazil", { x: 0.6, y: 1.6, w: 6, h: 1.7, fontFace: HF, fontSize: 50, bold: true, color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 0.95, isTextBox: true });
    s.addText("Pre-salt projects, partners and new technology", { x: 0.6, y: 3.35, w: 6, h: 0.4, fontFace: BF, fontSize: 20, color: C.gold, margin: 0, isTextBox: true });
    s.addText("On Demand Ocean Bottom Nodes at Mero, optical data harvesting and the fleet behind Brazil's deepwater operations", { x: 0.6, y: 3.85, w: 5.2, h: 0.6, fontFace: BF, fontSize: 12, color: C.muted, margin: 0, valign: "top", isTextBox: true });
    s.addText("Based on trade press and company news to September 2026", { x: 0.6, y: 5.05, w: 5, h: 0.25, fontFace: BF, fontSize: 9, color: C.dim, margin: 0, isTextBox: true });
    // seabed node array in the sonar rings
    const cx = 8.1, cy = 2.8;
    for (let r = 0; r < 4; r++) for (let c = 0; c < 5; c++) {
      const x = cx - 1.1 + c * 0.55 + (r % 2 ? 0.27 : 0), y = cy - 0.8 + r * 0.5;
      const gold = (r * 5 + c) % 4 === 1;
      s.addShape(pres.shapes.OVAL, { x, y, w: 0.13, h: 0.13, fill: { color: gold ? C.gold : C.text }, line: { type: "none" } });
    }
    s.addNotes("Deck summarises Sonardyne's Brazil activity from trade press and company sources: Offshore Magazine, JPT, Marine Technology News, Kraken Robotics releases and Sonardyne news.");
  }

  // ---------- 2. At a glance ----------
  {
    const s = contentSlide(2, "At a glance", "Three things to know");
    const items = [
      ["20+", "years in Brazil", "Local office, in-country support and Portuguese-speaking engineers since the 2000s", I.pin],
      ["84", "OD OBNs at Mero", "First field deployment of On Demand Ocean Bottom Nodes, early 2026", I.anchor],
      ["2027", "commercial production", "Scale-up could mean hundreds or thousands of nodes per field", I.rocket],
    ];
    items.forEach(([big, label, body, ic], i) => {
      const x = 0.5 + i * 3.07, y = 1.55, w = 2.86, h = 3.3;
      card(s, x, y, w, h);
      iconDot(s, ic, x + 0.3, y + 0.3, 0.55, C.greenDk);
      s.addText(big, { x: x + 0.3, y: y + 1.0, w: w - 0.6, h: 0.9, fontFace: HF, fontSize: 48, bold: true, color: C.gold, margin: 0, isTextBox: true });
      s.addText(label, { x: x + 0.3, y: y + 1.9, w: w - 0.6, h: 0.35, fontFace: BF, fontSize: 15, bold: true, color: C.white, margin: 0, isTextBox: true });
      s.addText(body, { x: x + 0.3, y: y + 2.3, w: w - 0.6, h: 0.8, fontFace: BF, fontSize: 11.5, color: C.muted, margin: 0, valign: "top", isTextBox: true });
    });
    s.addNotes("Executive summary. Sonardyne has had a local presence in Brazil for more than 20 years; the flagship OD OBN programme reached its first field deployment at the Petrobras-operated Mero field in early 2026; Kraken Robotics expects commercial production from 2027.");
  }

  // ---------- 3. Timeline ----------
  {
    const s = contentSlide(3, "Our history", "Two decades on the ground built today's trust");
    const ev = [
      ["2015", "Second office opens in central Rio, alongside the Rio das Ostras base"],
      ["2016", "Ranger 2 + GyroUSBL 7000 on Fugro Aquarius for Petrobras ROV work to 3,000 m"],
      ["2018", "OD OBN programme starts with Shell, Petrobras and SENAI CIMATEC"],
      ["2020", "Orders from OceanPact and C-Innovation (six vessels)"],
      ["2025", "OD OBN final tests after 2,000+ days of deepwater trials"],
      ["2026", "First 84 OD OBNs deployed at Mero"],
    ];
    const x0 = 1.0, x1 = 9.0, ly = 2.1, step = (x1 - x0) / (ev.length - 1);
    s.addShape(pres.shapes.LINE, { x: x0, y: ly, w: x1 - x0, h: 0, line: { color: C.line, width: 2 } });
    ev.forEach(([yr, t], i) => {
      const cx = x0 + i * step, last = i === ev.length - 1;
      s.addShape(pres.shapes.OVAL, { x: cx - 0.11, y: ly - 0.11, w: 0.22, h: 0.22, fill: { color: last ? C.gold : C.green }, line: { color: C.deep, width: 2 } });
      s.addText(yr, { x: cx - 0.7, y: ly - 0.62, w: 1.4, h: 0.4, fontFace: HF, fontSize: 18, bold: true, color: last ? C.gold : C.white, align: "center", margin: 0, isTextBox: true });
      s.addText(t, { x: cx - 0.74, y: ly + 0.25, w: 1.48, h: 1.1, fontFace: BF, fontSize: 10.5, color: C.muted, align: "center", valign: "top", margin: 0, isTextBox: true });
    });
    card(s, 0.5, 3.75, 9, 1.2, C.cardHi);
    iconDot(s, I.quoteN, 0.8, 4.05, 0.6, C.gold);
    s.addText([
      { text: "Portuguese-speaking support staff are a key reason operators stay with Sonardyne.", options: { bold: true, color: C.white, fontSize: 14, breakLine: true } },
      { text: "C-Innovation, 2022 case study. Sonardyne Brasil Ltda kept its office open through downturns and COVID-19.", options: { color: C.muted, fontSize: 10.5 } },
    ], { x: 1.65, y: 3.9, w: 7.6, h: 0.9, fontFace: BF, valign: "middle", margin: 0, isTextBox: true });
    s.addNotes("Office details from Sonardyne's May 2015 release. C-Innovation case study published October 2022. Mero deployment reported by JPT (June 2026) and Kraken Robotics (July 2026). Sonardyne Brasil Ltda provides in-country technical support, repair, training and sales.");
  }

  // ---------- 4. Partners ----------
  {
    const s = contentSlide(4, "Ecosystem", "Operators, researchers and vessel owners");
    const cols = [
      ["Operators", I.industry, [["Petrobras", "Mero operator; R&D via CENPES"], ["Shell Brasil", "Co-leads OD OBN; 19.3% of Mero"], ["Karoon Energy", "Client for C-Innovation's Cabo Frio"]]],
      ["Research & funding", I.flask, [["SENAI CIMATEC", "Co-manufactures nodes at Camaçari"], ["ANP", "Regulator; funds OD OBN via R&D clause"], ["Saipem", "FlatFish AUV harvests node data"]]],
      ["Vessel operators", I.ship, [["C-Innovation", "ROV/IMR fleet: Ranger 2, SPRINT-Nav, Fusion 2"], ["Fugro", "Fugro Aquarius: Ranger 2 + GyroUSBL 7000"], ["OceanPact", "Ranger 2 on geoscience vessels for Petrobras"]]],
    ];
    cols.forEach(([h, ic, rows], i) => {
      const x = 0.5 + i * 3.07, y = 1.45, w = 2.86;
      card(s, x, y, w, 3.5);
      iconDot(s, ic, x + 0.25, y + 0.25, 0.5, C.greenDk);
      s.addText(h, { x: x + 0.9, y: y + 0.25, w: w - 1.05, h: 0.5, fontFace: HF, fontSize: 14, bold: true, color: C.white, valign: "middle", margin: 0, isTextBox: true });
      rows.forEach(([name, d], j) => {
        const ry = y + 1.0 + j * 0.8;
        s.addText([
          { text: name, options: { bold: true, color: C.gold, fontSize: 13, breakLine: true } },
          { text: d, options: { color: C.muted, fontSize: 10.5 } },
        ], { x: x + 0.25, y: ry, w: w - 0.5, h: 0.7, fontFace: BF, valign: "top", margin: 0, isTextBox: true });
      });
    });
    s.addNotes("Petrobras: operator of Mero, R&D via CENPES, and client on Fugro and OceanPact charters. SENAI CIMATEC co-manufactures nodes at Camaçari and runs deployments. C-Innovation (Edison Chouest affiliate) also serves Shell, Chevron, ExxonMobil, BP and PetroRio in Brazil, according to Sonardyne's 2022 case study; its fleet using Sonardyne grew from 2 to 15 vessels.");
  }

  // ---------- 5. OD OBN stats ----------
  {
    const s = contentSlide(5, "Flagship project", "OD OBN: 4D monitoring without node recovery");
    s.addText("Semi-permanent seabed seismic nodes for low-cost 4D reservoir monitoring of the pre-salt", { x: 0.5, y: 1.15, w: 9, h: 0.3, fontFace: BF, fontSize: 13, italic: true, color: C.muted, margin: 0, isTextBox: true });
    const st = [["2,000+", "days of deepwater trials at Sapinhoá, Itapu and Búzios"], ["660", "pre-production nodes in the pilot array"], ["84", "nodes in the first Mero deployment, early 2026"], ["5 yrs", "design life on the seabed, rated to 3,000 m"]];
    st.forEach(([n, l], i) => {
      const x = 0.5 + i * 2.29, w = 2.1;
      card(s, x, 1.65, w, 1.75);
      s.addText(n, { x: x + 0.2, y: 1.8, w: w - 0.4, h: 0.75, fontFace: HF, fontSize: 34, bold: true, color: C.gold, margin: 0, isTextBox: true });
      s.addText(l, { x: x + 0.2, y: 2.6, w: w - 0.4, h: 0.7, fontFace: BF, fontSize: 11, color: C.text, valign: "top", margin: 0, isTextBox: true });
    });
    card(s, 0.5, 3.6, 9, 1.35, C.cardHi);
    s.addText("WHY IT MATTERS", { x: 0.8, y: 3.75, w: 3, h: 0.25, fontFace: BF, fontSize: 10, bold: true, color: C.green, charSpacing: 3, margin: 0, isTextBox: true });
    const why = [[I.down, "No repeat deployment and recovery: data is harvested wirelessly, on demand"], [I.globe, "Lower greenhouse-gas emissions from seismic acquisition and more offshore automation (Petrobras CENPES)"]];
    why.forEach(([ic, t], i) => {
      const x = 0.8 + i * 4.4;
      iconDot(s, ic, x, 4.15, 0.45, C.greenDk);
      s.addText(t, { x: x + 0.6, y: 4.05, w: 3.6, h: 0.65, fontFace: BF, fontSize: 12, color: C.white, valign: "middle", margin: 0, isTextBox: true });
    });
    s.addNotes("Figures: Offshore Magazine (Jan 2026), Marine Technology News, JPT (June 2026). Node life of up to five years and 3,000 m depth rating per JPT. Some sources give the pilot array as 600 nodes (2024 plan) and later 660 (2026).");
  }

  // ---------- 6. How it works (schematic) ----------
  {
    const s = contentSlide(6, "How it works", "Acoustics to control, optics to collect");
    // water column
    const top = 1.35, sea = 1.55, bed = 3.05;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: sea, w: 9, h: bed - sea, fill: { color: "0B3456", transparency: 20 }, line: { type: "none" } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: bed, w: 9, h: 0.28, fill: { color: "3A4A48" }, line: { type: "none" } });
    s.addShape(pres.shapes.LINE, { x: 0.5, y: sea, w: 9, h: 0, line: { color: "5FA8D3", width: 1.5 } });
    // vessel
    s.addShape(pres.shapes.TRAPEZOID, { x: 1.2, y: sea - 0.2, w: 1.1, h: 0.2, fill: { color: C.text }, line: { type: "none" }, rotate: 180 });
    s.addShape(pres.shapes.RECTANGLE, { x: 1.55, y: sea - 0.36, w: 0.35, h: 0.16, fill: { color: C.text }, line: { type: "none" } });
    s.addText("Survey vessel", { x: 2.4, y: top - 0.05, w: 1.5, h: 0.25, fontFace: BF, fontSize: 9, color: C.muted, margin: 0, isTextBox: true });
    // acoustic pings
    [0.35, 0.7, 1.05].forEach((r) => s.addShape(pres.shapes.ARC, { x: 1.75 - r, y: sea - r + 0.05, w: 2 * r, h: 2 * r, angleRange: [45, 135], line: { color: C.green, width: 1.25, dashType: "dash" }, fill: { type: "none" } }));
    s.addText("Acoustic command + clock sync", { x: 0.65, y: 2.7, w: 2.4, h: 0.25, fontFace: BF, fontSize: 9, color: C.green, bold: true, margin: 0, isTextBox: true });
    // nodes
    for (let i = 0; i < 12; i++) {
      const x = 1.0 + i * 0.72;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: bed - 0.12, w: 0.26, h: 0.14, rectRadius: 0.03, fill: { color: C.gold }, line: { type: "none" } });
    }
    s.addText("OD OBNs on the seabed, ~2,000 m", { x: 3.3, y: bed + 0.03, w: 3.4, h: 0.22, fontFace: BF, fontSize: 9, color: C.white, bold: true, align: "center", margin: 0, isTextBox: true });
    // AUV + optical beam
    s.addShape(pres.shapes.ISOSCELES_TRIANGLE, { x: 6.85, y: 2.3, w: 0.8, h: 0.62, fill: { color: "7CF5C8", transparency: 55 }, line: { type: "none" } });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.7, y: 2.05, w: 1.1, h: 0.3, rectRadius: 0.15, fill: { color: C.green }, line: { type: "none" } });
    s.addText("FlatFish AUV", { x: 7.9, y: 1.95, w: 1.5, h: 0.25, fontFace: BF, fontSize: 9, bold: true, color: C.white, margin: 0, isTextBox: true });
    s.addText("BlueComm optical download", { x: 7.9, y: 2.2, w: 1.5, h: 0.4, fontFace: BF, fontSize: 9, color: "7CF5C8", margin: 0, valign: "top", isTextBox: true });
    // steps
    const steps = [["1", "Deploy", "Nodes left over the reservoir for years", I.down], ["2", "Sync", "Acoustic commands start recording and sync clocks", I.wifi], ["3", "Record", "Capture energy reflected from the reservoir", I.wave], ["4", "Harvest", "AUV pulls data over a BlueComm optical link", I.bulb], ["5", "Process", "4D workflows track fluid movement", I.layers]];
    steps.forEach(([n, h, d, ic], i) => {
      const x = 0.5 + i * 1.83, w = 1.7, y = 3.55;
      card(s, x, y, w, 1.45);
      iconDot(s, ic, x + 0.15, y + 0.15, 0.38, i === 3 ? C.gold : C.greenDk);
      s.addText(`${n}  ${h}`, { x: x + 0.6, y: y + 0.15, w: w - 0.7, h: 0.38, fontFace: HF, fontSize: 11.5, bold: true, color: C.white, valign: "middle", margin: 0, isTextBox: true });
      s.addText(d, { x: x + 0.15, y: y + 0.63, w: w - 0.3, h: 0.75, fontFace: BF, fontSize: 10, color: C.muted, valign: "top", margin: 0, isTextBox: true });
    });
    s.addNotes("Two links, two jobs: acoustics for long-range control and timing; optics for short-range, high-volume data transfer. The data harvesting vehicle is Saipem's FlatFish AUV, with ROV retrieval as an alternative (Sonardyne case study). Results are used to adjust extraction rates and fluid reinjection (JPT). Schematic is illustrative, not to scale.");
  }

  // ---------- 7. Mero ----------
  {
    const s = contentSlide(7, "First field deployment", "Mero: first field deployment in the pre-salt");
    card(s, 0.5, 1.45, 4.3, 3.5);
    s.addText("Mero consortium share", { x: 0.75, y: 1.6, w: 3.8, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: C.white, margin: 0, isTextBox: true });
    const labels = ["Petrobras", "Shell Brasil", "TotalEnergies", "CNPC", "CNOOC", "PPSA"];
    const vals = [38.6, 19.3, 19.3, 9.65, 9.65, 3.5];
    const cols = [C.greenDk, C.gold, "5FA8D3", "7C93AD", "4F6B88", "33506E"];
    s.addChart(pres.charts.DOUGHNUT, [{ name: "Share", labels, values: vals }], {
      x: 0.6, y: 1.95, w: 2.3, h: 2.8, holeSize: 62, chartColors: cols, showLegend: false, showValue: false, showPercent: false, showLabel: false,
      dataBorder: { pt: 1, color: C.card }, showTitle: false,
    });
    s.addText([{ text: "38.6%", options: { fontSize: 20, bold: true, color: C.green, breakLine: true } }, { text: "Petrobras", options: { fontSize: 10, color: C.muted } }],
      { x: 1.15, y: 3.0, w: 1.2, h: 0.7, fontFace: HF, align: "center", valign: "middle", margin: 0, isTextBox: true });
    labels.forEach((l, i) => {
      const y = 2.15 + i * 0.4;
      s.addShape(pres.shapes.OVAL, { x: 3.0, y: y + 0.08, w: 0.14, h: 0.14, fill: { color: cols[i] }, line: { type: "none" } });
      s.addText([{ text: l + "  ", options: { color: C.text } }, { text: `${vals[i]}%`, options: { color: C.muted } }], { x: 3.22, y, w: 1.55, h: 0.3, fontFace: BF, fontSize: 10.5, margin: 0, valign: "middle", isTextBox: true });
    });
    // facts
    const facts = [[I.pin, "Santos Basin pre-salt, ~2,000 m water depth"], [I.anchor, "First 84 nodes of the pilot batch placed early 2026"], [I.rocket, "Commercial production expected 2027"]];
    facts.forEach(([ic, t], i) => {
      const y = 1.5 + i * 0.55;
      iconDot(s, ic, 5.1, y, 0.4, C.greenDk);
      s.addText(t, { x: 5.65, y, w: 3.85, h: 0.4, fontFace: BF, fontSize: 12.5, color: C.white, valign: "middle", margin: 0, isTextBox: true });
    });
    card(s, 5.1, 3.25, 4.4, 1.7, C.cardHi);
    s.addText("“Seeing the OD OBN system successfully deployed at Mero is a strong validation of the technology and the collaborative R&D behind it.”", { x: 5.35, y: 3.35, w: 3.95, h: 1.1, fontFace: BF, fontSize: 12.5, italic: true, color: C.white, valign: "middle", margin: 0, isTextBox: true });
    s.addText("Shaun Dunn, Sonardyne (JPT, June 2026)", { x: 5.35, y: 4.5, w: 3.95, h: 0.3, fontFace: BF, fontSize: 10, color: C.gold, margin: 0, isTextBox: true });
    s.addNotes("Next steps: seismic acquisition over the monitored area, optical data retrieval, 4D processing and assessment of reservoir-management value. Shell Brasil's Manoela Lopes called the Mero deployment a decisive step in maturing the technology.");
  }

  // ---------- 8. Technology ----------
  {
    const s = contentSlide(8, "Technology", "Four building blocks behind the programme");
    const blocks = [
      ["BlueComm optical comms", I.bulb, "2.5–10 Mbps", "up to 75 m; rated to 4,000 m. 9 GB+ moved on one lithium D-cell"],
      ["Wideband acoustic control", I.wifi, "100s of nodes", "Long-range commands and seismic-grade clock sync, from 6G heritage"],
      ["Resident AUV harvesting", I.robot, "No recovery", "Saipem FlatFish collects data wirelessly; ROV retrieval as fallback"],
      ["Made in Brazil", I.industry, "600 / year", "Planned capacity at CIMATEC PARK, Camaçari, Bahia"],
    ];
    blocks.forEach(([h, ic, big, d], i) => {
      const x = 0.5 + (i % 2) * 4.6, y = 1.45 + Math.floor(i / 2) * 1.8, w = 4.4, hh = 1.6;
      card(s, x, y, w, hh);
      iconDot(s, i % 2 ? I[Object.keys(I).find(k => I[k] === ic) + "N"] : ic, x + 0.25, y + 0.25, 0.5, i % 2 ? C.gold : C.greenDk);
      s.addText(h, { x: x + 0.9, y: y + 0.25, w: 3.3, h: 0.5, fontFace: HF, fontSize: 13.5, bold: true, color: C.white, valign: "middle", margin: 0, isTextBox: true });
      s.addText(big, { x: x + 0.25, y: y + 0.85, w: 1.85, h: 0.55, fontFace: HF, fontSize: 16, bold: true, color: C.gold, valign: "middle", margin: 0, isTextBox: true });
      s.addText(d, { x: x + 2.15, y: y + 0.82, w: 2.05, h: 0.65, fontFace: BF, fontSize: 10.5, color: C.muted, valign: "middle", margin: 0, isTextBox: true });
    });
    s.addNotes("Press coverage names BlueComm as the optical system but does not state which model the nodes use; the BlueComm 200 UV figures are Sonardyne's current product specs. Sonardyne leads communications, integration and co-manufacturing. Plant capacity of 600 nodes a year is from the 2024 announcement.");
  }

  // ---------- 9. Fleet ----------
  {
    const s = contentSlide(9, "Vessel positioning", "Positioning Brazil's deepwater fleet");
    const sys = [
      ["Ranger 2 USBL", "C-Innovation, Fugro, OceanPact", "Tracks ROVs, corers and towed sensors; DP reference", I.crosshair],
      ["GyroUSBL 7000", "Fugro Aquarius", "Transceiver + survey-grade INS in one unit, to 3,000 m", I.compass],
      ["SPRINT-Nav", "C-Innovation", "Pre-calibrated INS, DVL and depth; cuts ROV set-up time", I.cog],
      ["Fusion 2 LBL", "C-Innovation", "Real-time SLAM calibration; fewer Compatts to deploy", I.satellite],
    ];
    sys.forEach(([n, u, d, ic], i) => {
      const x = 0.5 + (i % 2) * 2.95, y = 1.45 + Math.floor(i / 2) * 1.78, w = 2.8, h = 1.6;
      card(s, x, y, w, h);
      iconDot(s, ic, x + 0.2, y + 0.2, 0.42, C.greenDk);
      s.addText(n, { x: x + 0.72, y: y + 0.2, w: w - 0.85, h: 0.42, fontFace: HF, fontSize: 12.5, bold: true, color: C.white, valign: "middle", margin: 0, isTextBox: true });
      s.addText(u, { x: x + 0.2, y: y + 0.72, w: w - 0.4, h: 0.25, fontFace: BF, fontSize: 10, bold: true, color: C.gold, margin: 0, isTextBox: true });
      s.addText(d, { x: x + 0.2, y: y + 0.98, w: w - 0.4, h: 0.55, fontFace: BF, fontSize: 10, color: C.muted, valign: "top", margin: 0, isTextBox: true });
    });
    // benchmark
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.5, y: 1.45, w: 3.0, h: 3.38, rectRadius: 0.08, fill: { color: C.greenDk }, line: { type: "none" } });
    s.addText("THE BENCHMARK", { x: 6.75, y: 1.65, w: 2.5, h: 0.25, fontFace: BF, fontSize: 10, bold: true, color: "CFF5E6", charSpacing: 3, margin: 0, isTextBox: true });
    s.addText("< 5 m", { x: 6.75, y: 2.0, w: 2.5, h: 0.9, fontFace: HF, fontSize: 48, bold: true, color: C.white, margin: 0, isTextBox: true });
    s.addText("error at 1,000 m water depth", { x: 6.75, y: 2.9, w: 2.5, h: 0.3, fontFace: BF, fontSize: 13, bold: true, color: C.white, margin: 0, isTextBox: true });
    s.addText("95% of positions within 0.5% of water depth, while the vessel is moving", { x: 6.75, y: 3.4, w: 2.5, h: 1.0, fontFace: BF, fontSize: 11.5, color: "E4F7EF", valign: "top", margin: 0, isTextBox: true });
    s.addNotes("C-Innovation's Sonardyne-equipped fleet in Brazil grew from 2 to 15 vessels (2022 case study). Its 2020 order covered SPRINT, Lodestar AHRS, Syrinx DVL, SPRINT-Nav, Compatt 6+ and WSM 6+ for six vessels working for Petrobras and Karoon.");
  }

  // ---------- 10. Roadmap ----------
  {
    const s = contentSlide(10, "Roadmap", "What comes next");
    const st = [["Survey & retrieve", "Seismic shoot over Mero, then optical data recovery from the nodes", I.search, "NOW"],
      ["Prove the value", "4D processing and assessment of how the data supports reservoir management", I.chart, "NEXT"],
      ["Scale up", "Commercial production from 2027; full fields may need hundreds or thousands of nodes", I.industry, "2027+"],
      ["Kraken ownership", "Sonardyne joined Kraken Robotics with the Covelya acquisition on 2 July 2026", I.hand, "CONTEXT"]];
    st.forEach(([h, d, ic, tag], i) => {
      const x = 0.5 + i * 2.29, w = 2.1, y = 1.6;
      card(s, x, y, w, 3.25, i === 3 ? C.cardHi : C.card);
      s.addText(tag, { x: x + 0.25, y: y + 0.25, w: 1.6, h: 0.25, fontFace: BF, fontSize: 10, bold: true, color: i === 3 ? C.gold : C.green, charSpacing: 3, margin: 0, isTextBox: true });
      iconDot(s, i === 3 ? I.handN : ic, x + 0.25, y + 0.65, 0.6, i === 3 ? C.gold : C.greenDk);
      s.addText(h, { x: x + 0.25, y: y + 1.4, w: w - 0.4, h: 0.6, valign: "top", fontFace: HF, fontSize: 14, bold: true, color: C.white, margin: 0, isTextBox: true });
      s.addText(d, { x: x + 0.25, y: y + 2.05, w: w - 0.45, h: 1.05, fontFace: BF, fontSize: 11, color: C.muted, valign: "top", margin: 0, isTextBox: true });
    });
    s.addNotes("Commercial production timing and scale from Kraken Robotics' 20 July 2026 business update.");
  }

  // ---------- 11. Takeaways ----------
  {
    const s = pres.addSlide();
    s.background = { path: path.join(__dirname, "bg_title.png") };
    s.addText("KEY TAKEAWAYS", { x: 0.6, y: 0.7, w: 5, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: C.green, charSpacing: 4, margin: 0, isTextBox: true });
    s.addText("Brazil is where next-generation seabed monitoring goes live", { x: 0.6, y: 1.05, w: 6.6, h: 1.2, fontFace: HF, fontSize: 28, bold: true, color: C.white, margin: 0, valign: "top", isTextBox: true });
    const t = [["01", "Local presence and Portuguese-speaking support underpin long-term operator relationships"],
      ["02", "OD OBN has moved from 2,000+ days of trials to a live deployment at Mero"],
      ["03", "Acoustic control and optical harvesting make repeat 4D surveys cheaper and lower-emission"]];
    t.forEach(([n, x], i) => {
      const y = 2.65 + i * 0.75;
      s.addText(n, { x: 0.6, y, w: 0.7, h: 0.6, fontFace: HF, fontSize: 24, bold: true, color: C.gold, margin: 0, valign: "middle", isTextBox: true });
      s.addText(x, { x: 1.35, y, w: 5.3, h: 0.6, fontFace: BF, fontSize: 14, color: C.text, margin: 0, valign: "middle", isTextBox: true });
    });
    s.addNotes("Closing summary. Invite questions on the Mero timeline, the scale-up to commercial production from 2027, and what Kraken Robotics ownership means for the Brazil business.");
  }

  // ---------- 12. Sources ----------
  {
    const s = contentSlide(12, "References", "Sources");
    const src = [
      "JPT (SPE), 19 June 2026: New seismic acquisition technology advances offshore Brazil",
      "Kraken Robotics, 20 July 2026: $35 million in new orders and business update",
      "Offshore Magazine, 15 Jan 2026: On-demand OBN system enhances surveillance of Brazil's presalt fields",
      "Marine Technology News: On-Demand Ocean Bottom Node, a new era in deepwater seismic monitoring",
      "Sonardyne: OD OBN case study; OD OBN phase release (June 2024); C-Innovation case study (Oct 2022); OceanPact release (June 2020); second Brazil office (May 2015); BlueComm 200 UV product page",
      "Offshore Magazine, Sept 2016: Sonardyne delivers subsea technology to Fugro vessel offshore Brazil",
      "Keyfacts Energy, Oct 2020: C-Innovation selects Sonardyne technology",
    ];
    s.addText(src.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < src.length - 1 } })), { x: 0.5, y: 1.35, w: 9, h: 3.2, fontFace: BF, fontSize: 11.5, color: C.text, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true });
    s.addText("Node counts differ between sources over time (600 planned in 2024; 660 in production in 2026).", { x: 0.5, y: 4.75, w: 9, h: 0.3, fontFace: BF, fontSize: 10, italic: true, color: C.muted, margin: 0, isTextBox: true });
  }

  await pres.writeFile({ fileName: path.join(__dirname, "raw.pptx") });
  console.log("written");
})();
