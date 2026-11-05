// 갤럭시 카메라 무음 사용 설명서 PPT 생성
// node build_deck.js <스크린샷 폴더> <출력 pptx>
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { setTheme } = require("./set_theme");

const [SHOTS, OUT] = process.argv.slice(2);

const THEME = {
  name: "Galaxy Camera Mute",
  headFontFace: "맑은 고딕",
  bodyFontFace: "맑은 고딕",
  colors: {
    dk1: "1F2330", lt1: "FFFFFF", dk2: "3A3F55", lt2: "F3F4F8",
    accent1: "5B4FE9", accent2: "1E9E6A", accent3: "D98E04", accent4: "D64545",
    accent5: "8A8FA3", accent6: "EDEBFD", hlink: "5B4FE9", folHlink: "3A3F55",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "갤럭시 카메라 무음 사용 설명서";
pres.subject = "사용 설명서";
const C = pres.SchemeColor;

const W = 13.333;
const MX = 0.6;

// ------------------------------------------------------------------ 레이아웃
pres.defineSlideMaster({
  title: "COVER",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 2.2, w: 6.4, h: 1.3, fontSize: 44, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: MX, y: 3.65, w: 6.4, h: 2.2, fontSize: 18, color: "C9CCDA", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECTION",
  background: { color: HEX.accent1 },
  objects: [
    { placeholder: { options: { name: "num", type: "body", x: MX, y: 2.1, w: 4, h: 1.1, fontSize: 60, bold: true, color: "C9C4FA", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 3.2, w: 12, h: 1.0, fontSize: 40, bold: true, color: C.background1, align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: MX, y: 4.3, w: 11, h: 1.0, fontSize: 18, color: "E4E1FD", margin: 0, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.35, w: 12.1, h: 0.8, fontSize: 30, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "갤럭시 카메라 무음 · 사용 설명서", options: { x: MX, y: 7.02, w: 6, h: 0.3, fontSize: 10, color: HEX.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 12.13, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: HEX.accent5, align: "right" },
});

// ------------------------------------------------------------------ 도우미
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
const shot = (n) => path.join(SHOTS, n);
const shadow = () => ({ type: "outer", color: "1F2330", opacity: 0.18, blur: 8, offset: 2, angle: 90 });

// 둥근 카드 위에 스크린샷. w 또는 h 중 하나로 크기를 정한다. 실제 배치 영역을 돌려준다.
function picture(slide, file, { x, y, w, h, pad = 0.08, name }) {
  const s = pngSize(shot(file));
  if (w && !h) h = (w - 2 * pad) * s.h / s.w + 2 * pad;
  else if (h && !w) w = (h - 2 * pad) * s.w / s.h + 2 * pad;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08, fill: { color: C.background1 },
    line: { color: "E2E4EC", width: 0.75 }, shadow: shadow(), objectName: `${name}-card`,
  });
  slide.addImage({ path: shot(file), x: x + pad, y: y + pad, w: w - 2 * pad, h: h - 2 * pad, objectName: name, altText: name });
  return { x, y, w, h, iw: w - 2 * pad, ix: x + pad, iy: y + pad, px: s.w };
}

function badge(slide, n, x, y, d = 0.42, color = C.accent1) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { color: C.background1, width: 1.5 }, objectName: `badge-${n}` });
  slide.addText(String(n), { x, y, w: d, h: d, fontSize: d > 0.4 ? 15 : 12, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
}

function text(slide, t, opts) {
  slide.addText(t, Object.assign({ fontSize: 15, color: C.text2, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 4 }, opts));
}

function bullets(slide, items, opts) {
  const runs = items.map((it, i) => {
    const o = { bullet: { indent: 16 }, breakLine: i < items.length - 1 };
    if (typeof it === "string") return { text: it, options: o };
    return { text: it.text, options: Object.assign(o, it.options || {}) };
  });
  slide.addText(runs, Object.assign({ fontSize: 15, color: C.text2, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 8 }, opts));
}

// 번호 + 굵은 제목 + 설명 한 줄 묶음
function stepRow(slide, n, head, body, x, y, w, color = C.accent1) {
  badge(slide, n, x, y, 0.42, color);
  slide.addText(head, { x: x + 0.58, y: y - 0.02, w: w - 0.58, h: 0.45, fontSize: 17, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  if (body) text(slide, body, { x: x + 0.58, y: y + 0.45, w: w - 0.58, h: 0.75, fontSize: 14 });
}

function card(slide, x, y, w, h, fill = C.background2, name = "card") {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill }, objectName: name });
}

function note(slide, t, x, y, w, h, kind = "warn") {
  const fill = { warn: "FFF4DC", ok: "E3F5EC", info: HEX.accent6, danger: "FDE8E8" }[kind];
  const ink = { warn: "8A5A00", ok: "136B47", info: "3B30B8", danger: "A32B2B" }[kind];
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line: { color: fill }, objectName: `note-${kind}` });
  slide.addText(t, { x: x + 0.22, y: y + 0.12, w: w - 0.44, h: h - 0.24, fontSize: 14, color: ink, valign: "middle", margin: 0, isTextBox: true });
}

let section = "";
function content(title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  return s;
}
function divider(num, title, body) {
  section = title;
  pres.addSection({ title });
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle: section });
  s.addText(num, { placeholder: "num" });
  s.addText(title, { placeholder: "title" });
  s.addText(body, { placeholder: "body" });
  return s;
}

// ================================================================== 표지
section = "표지";
pres.addSection({ title: "표지" });
{
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: section });
  s.addText("갤럭시 카메라 무음", { placeholder: "title" });
  s.addText([
    { text: "사용 설명서 · v1.0.1", options: { bold: true, color: "FFFFFF", breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "ADB로 삼성 갤럭시의 카메라 셔터음 강제 설정을 해제하고, 카메라를 켤 때 소리 모드를 무음으로 바꾸는 빅스비 루틴까지 한 번에 추가합니다.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "2026년 11월", options: { fontSize: 14, color: "8A8FA3" } },
  ], { placeholder: "body" });
  picture(s, "app_04_muted.png", { x: 7.9, y: 0.75, h: 6.0, name: "표지 화면" });
}

// ================================================================== 목차
section = "표지";
{
  const s = content("목차");
  const items = [
    ["1", "시작하기 전에", "프로그램이 하는 일, 준비물, 주의사항"],
    ["2", "휴대폰 준비 (처음 한 번만)", "개발자 모드 · 보안 위험 자동 차단 끄기 · USB 디버깅 켜기"],
    ["3", "프로그램 사용하기", "실행, 화면 구성, 무음 적용, 빅스비 루틴 저장, 원래대로 되돌리기"],
    ["4", "문제 해결과 마무리", "증상별 해결 방법, 사용 후 정리, 자주 묻는 질문"],
  ];
  items.forEach(([n, h, b], i) => {
    const x = MX + (i % 2) * 6.15, y = 1.55 + Math.floor(i / 2) * 2.6;
    card(s, x, y, 5.95, 2.3, C.background2, `toc-${n}`);
    s.addText(n, { x: x + 0.35, y: y + 0.3, w: 1.2, h: 0.9, fontSize: 44, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(h, { x: x + 0.35, y: y + 1.15, w: 5.3, h: 0.45, fontSize: 20, bold: true, color: C.text1, margin: 0, isTextBox: true });
    text(s, b, { x: x + 0.35, y: y + 1.6, w: 5.3, h: 0.55, fontSize: 14 });
  });
}

// ================================================================== 1. 시작하기 전에
divider("01", "시작하기 전에", "이 프로그램이 무엇을 하는지, 무엇이 필요한지 먼저 확인하세요.");
{
  const s = content("이 프로그램이 하는 일");
  // 왼쪽: 두 가지 기능
  card(s, MX, 1.45, 6.6, 2.55, C.background2, "기능1");
  badge(s, 1, MX + 0.3, 1.7);
  s.addText("카메라 셔터음 강제 설정 해제", { x: MX + 0.9, y: 1.68, w: 5.5, h: 0.45, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
  text(s, "한국판 갤럭시는 셔터음이 강제로 켜져 있습니다. 이 설정값을 USB(ADB)로 바꿔 셔터음이 나지 않게 합니다. 루팅이 필요 없고, 휴대폰에 앱을 설치하지도 않습니다.", { x: MX + 0.9, y: 2.18, w: 5.5, h: 1.0, fontSize: 14 });
  s.addText("settings put system csc_pref_camera_forced_shuttersound_key 0", { x: MX + 0.9, y: 3.25, w: 5.5, h: 0.5, fontFace: "Consolas", fontSize: 11, color: C.text1, fill: { color: C.background1 }, margin: 6, valign: "middle", isTextBox: true });

  card(s, MX, 4.2, 6.6, 2.55, C.background2, "기능2");
  badge(s, 2, MX + 0.3, 4.45);
  s.addText("빅스비 루틴 함께 추가", { x: MX + 0.9, y: 4.43, w: 5.5, h: 0.45, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
  text(s, "카메라 앱을 켜면 소리 모드를 무음으로, 끄면 원래대로 되돌리는 루틴을 휴대폰의 '모드 및 루틴' 앱에 띄워 줍니다. 휴대폰에서 [저장]만 누르면 추가됩니다. 셔터음 해제와 함께 쓰면 더 확실합니다.", { x: MX + 0.9, y: 4.93, w: 5.5, h: 1.6, fontSize: 14 });

  // 오른쪽: 연결 흐름
  const fx = 7.75;
  const boxes = [["PC", "이 프로그램 실행"], ["USB 케이블", "ADB 명령 전달"], ["갤럭시", "설정 변경 · 루틴 추가"]];
  boxes.forEach(([h, b], i) => {
    const y = 1.55 + i * 1.8;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: fx, y, w: 4.95, h: 1.25, rectRadius: 0.12, fill: { color: i === 1 ? C.accent6 : C.background1 }, line: { color: i === 1 ? C.accent6 : "D9DCE6", width: 1 }, shadow: shadow(), objectName: `flow-${i}` });
    s.addText(h, { x: fx + 0.3, y: y + 0.18, w: 4.4, h: 0.45, fontSize: 18, bold: true, color: i === 1 ? C.accent1 : C.text1, margin: 0, isTextBox: true });
    text(s, b, { x: fx + 0.3, y: y + 0.65, w: 4.4, h: 0.4, fontSize: 14 });
    if (i < 2) s.addShape(pres.shapes.DOWN_ARROW, { x: fx + 2.25, y: y + 1.32, w: 0.45, h: 0.42, fill: { color: C.accent5 }, line: { color: C.accent5 }, objectName: `arrow-${i}` });
  });
}
{
  const s = content("준비물과 지원 환경");
  const items = [
    ["PC", "Windows 10 / 11", "설치 없이 GalaxyCameraMute.exe 하나만 실행합니다. Python 등 다른 프로그램이 필요 없습니다."],
    ["폰", "삼성 갤럭시", "One UI 기기. 빅스비 루틴 기능은 '모드 및 루틴' 앱이 있는 기기에서 동작합니다."],
    ["선", "USB 데이터 케이블", "충전 전용 케이블은 안 됩니다. 휴대폰을 PC에서 파일로 열 수 있는 케이블을 쓰세요."],
    ["망", "인터넷 (처음 한 번)", "처음 실행할 때 Google 공식 서버에서 ADB 도구(약 10MB)를 내려받습니다."],
  ];
  items.forEach(([ic, h, b], i) => {
    const x = MX + (i % 2) * 6.15, y = 1.5 + Math.floor(i / 2) * 2.35;
    card(s, x, y, 5.95, 2.1, C.background2, `need-${i}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.3, w: 0.8, h: 0.8, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `need-icon-${i}` });
    s.addText(ic, { x: x + 0.3, y: y + 0.3, w: 0.8, h: 0.8, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(h, { x: x + 1.3, y: y + 0.32, w: 4.4, h: 0.45, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
    text(s, b, { x: x + 1.3, y: y + 0.82, w: 4.4, h: 1.15, fontSize: 14 });
  });
  note(s, "루팅이 필요 없고 휴대폰에 앱을 설치하지 않습니다. 바꾸는 것은 설정값 하나이며, 언제든 [셔터음 원복]으로 되돌릴 수 있습니다.", MX, 6.25, 12.1, 0.6, "ok");
}
{
  const s = content("꼭 읽어주세요");
  const rows = [
    ["본인 소유 기기에만 사용하세요", "회사·학교 등에서 관리하는 기기나 다른 사람의 휴대폰에는 사용하지 마세요.", C.accent4],
    ["타인의 동의 없는 촬영은 처벌받습니다", "셔터음 설정 변경 자체는 불법이 아니지만(이동통신 사업자 자율 규약), 동의 없는 촬영은 성폭력처벌법 등으로 처벌될 수 있습니다.", C.accent4],
    ["소프트웨어 업데이트 후 다시 적용", "One UI 업데이트나 초기화 뒤에는 설정이 원래대로 돌아갈 수 있습니다. 그때는 다시 [카메라 무음 적용]을 누르면 됩니다.", C.accent3],
    ["사용 후 USB 디버깅은 꺼두세요", "적용과 확인이 끝나면 USB 디버깅과 개발자 옵션을 다시 끄는 것이 안전합니다. 셔터음 설정은 그대로 유지됩니다.", C.accent2],
  ];
  rows.forEach(([h, b, col], i) => {
    const y = 1.4 + i * 1.27;
    card(s, MX, y, 12.1, 1.15, C.background2, `warn-${i}`);
    badge(s, "!", MX + 0.3, y + 0.39, 0.42, col);
    s.addText(h, { x: MX + 0.95, y: y + 0.16, w: 10.9, h: 0.42, fontSize: 17, bold: true, color: C.text1, margin: 0, isTextBox: true });
    text(s, b, { x: MX + 0.95, y: y + 0.6, w: 10.9, h: 0.5, fontSize: 14 });
  });
  text(s, "본 소프트웨어는 삼성전자 및 Google과 제휴 관계가 없으며, 사용으로 인해 발생하는 문제에 대해 저작자는 책임지지 않습니다.", { x: MX, y: 6.95 - 0.35, w: 12.1, h: 0.3, fontSize: 11, color: C.accent5 });
}

// ================================================================== 2. 휴대폰 준비
divider("02", "휴대폰 준비 (처음 한 번만)", "USB 디버깅을 켜서 PC가 휴대폰에 명령을 보낼 수 있게 합니다. 한 번 해두면 다음부터는 건너뜁니다.");
{
  const s = content("전체 흐름 한눈에 보기");
  const steps = ["설정 앱 열기", "폰 정보 열기", "빌드번호 7번 누르기", "보안 및 개인정보 보호", "보안 위험 자동 차단 끄기", "개발자 옵션", "USB 디버깅 켜기", "PC 인증 허용"];
  const groups = [["개발자 모드 켜기", 0, 3, C.accent1], ["보안 차단 해제", 3, 5, C.accent4], ["USB 디버깅 켜기", 5, 8, C.accent2]];
  const cw = 1.42, gap = 0.1, x0 = MX + 0.05;
  steps.forEach((t, i) => {
    const x = x0 + i * (cw + gap);
    const g = groups.find((gg) => i >= gg[1] && i < gg[2]);
    card(s, x, 2.35, cw, 2.2, C.background2, `flow-step-${i + 1}`);
    badge(s, i + 1, x + cw / 2 - 0.25, 2.6, 0.5, g[3]);
    s.addText(t, { x: x + 0.1, y: 3.3, w: cw - 0.2, h: 1.1, fontSize: 14, bold: true, color: C.text1, align: "center", valign: "top", margin: 0, isTextBox: true });
  });
  groups.forEach(([t, a, b, col]) => {
    const x = x0 + a * (cw + gap), w = (b - a) * (cw + gap) - gap;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.55, w, h: 0.55, rectRadius: 0.1, fill: { color: col }, line: { color: col }, objectName: `group-${t}` });
    s.addText(t, { x, y: 1.55, w, h: 0.55, fontSize: 15, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
  });
  note(s, "막히는 곳의 대부분은 5단계입니다. '보안 위험 자동 차단'이 켜져 있으면 7단계의 USB 디버깅 스위치가 회색으로 잠겨 켜지지 않습니다.", MX, 4.95, 12.1, 0.75, "warn");
  text(s, "프로그램 오른쪽 위 [설정 방법] 버튼을 누르면 같은 내용을 사진과 함께 단계별로 볼 수 있습니다.", { x: MX, y: 6.0, w: 12.1, h: 0.4, fontSize: 14 });
}

const GUIDE = [
  ["설정 앱 열기", "guide_01_settings_app.png", "홈 화면 가운데를 위로 쓸어올려 앱 목록을 연 뒤, 빨간 네모의 [설정](톱니바퀴)을 누릅니다.", "화면 위에서 아래로 두 번 쓸어내린 뒤 오른쪽 위 톱니바퀴를 눌러도 됩니다."],
  ["폰 정보 열기", "guide_02_about_phone.png", "설정 목록을 맨 아래까지 내려 [폰 정보]를 누릅니다. 기종에 따라 [휴대전화 정보]로 보이기도 합니다.", "사진에 보이는 [개발자 옵션]은 3단계를 마쳐야 생깁니다. 지금 없는 것이 정상입니다."],
  ["빌드번호 7번 누르기", "guide_03_build_number.png", "[소프트웨어 정보]로 들어가 [빌드번호]를 7번 연속으로 누릅니다. '개발자 모드를 켰습니다'가 뜨면 성공입니다.", "화면 잠금을 쓰는 경우 PIN·패턴을 한 번 입력해야 합니다."],
  ["보안 및 개인정보 보호 열기", "guide_04_security_menu.png", "설정 목록에서 [보안 및 개인정보 보호]를 누릅니다.", "'보안 위험 자동 차단'이 켜져 있으면 USB 디버깅을 켤 수 없으므로 먼저 이 기능을 끕니다."],
  ["보안 위험 자동 차단 끄기", "guide_05_auto_blocker.png", "[보안 위험 자동 차단]에 들어가 맨 위 스위치를 꺼서 [사용 안 함]으로 만듭니다.", "아래쪽 [자동으로 켜기]도 함께 끄세요. 켜 두면 30분 뒤 차단이 다시 켜져 연결이 끊깁니다."],
  ["개발자 옵션 들어가기", "guide_06_developer_options.png", "설정으로 돌아와 맨 아래까지 내리면 [개발자 옵션]이 새로 생겨 있습니다. 눌러서 들어갑니다.", "항목이 안 보이면 3단계의 빌드번호 누르기를 다시 해보세요."],
  ["USB 디버깅 켜기", "guide_07_usb_debugging.png", "아래로 내려 [디버깅] 항목의 [USB 디버깅]을 켭니다. 그다음 USB 케이블로 PC와 연결합니다.", "스위치가 회색이면 5단계가 아직 안 된 것입니다. 연결 모드를 물으면 [파일 전송]을 고르세요."],
  ["PC 인증 허용하기", "guide_08_allow_popup.png", "케이블을 연결하면 'USB 디버깅을 허용하시겠습니까?' 팝업이 뜹니다. [이 컴퓨터에서 항상 허용]을 체크하고 [허용]을 누릅니다.", "팝업이 안 보이면 케이블을 뽑았다가 다시 꽂아보세요. (사진은 예시 화면)"],
];
for (let p = 0; p < 4; p++) {
  const a = GUIDE[p * 2], b = GUIDE[p * 2 + 1];
  const s = content(`${p * 2 + 1}~${p * 2 + 2}단계 · ${a[0]} / ${b[0]}`);
  [a, b].forEach((g, k) => {
    const n = p * 2 + k + 1;
    const y = 1.4 + k * 2.8;
    const pic = picture(s, g[1], { x: MX, y, h: 2.55, name: `${n}단계 화면` });
    const tx = MX + pic.w + 0.45, tw = 12.1 - pic.w - 0.45;
    badge(s, n, tx, y + 0.08, 0.5, n === 5 ? C.accent4 : C.accent1);
    s.addText(`${n}단계 · ${g[0]}`, { x: tx + 0.68, y: y + 0.08, w: tw - 0.68, h: 0.5, fontSize: 20, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    text(s, g[2], { x: tx, y: y + 0.78, w: tw, h: 0.95, fontSize: 15, color: C.text1 });
    note(s, g[3], tx, y + 1.75, tw, 0.75, n === 5 ? "danger" : "info");
  });
}
{
  const s = content("가장 많이 막히는 곳 · 보안 위험 자동 차단");
  const pic = picture(s, "guide_05_auto_blocker.png", { x: MX, y: 1.45, w: 6.0, name: "보안 위험 자동 차단" });
  // 두 스위치 위치 표시
  const sc = pic.iw / pic.px;
  badge(s, "A", pic.ix + 470 * sc, pic.iy + 18 * sc, 0.45, C.accent4);
  badge(s, "B", pic.ix + 470 * sc, pic.iy + 222 * sc, 0.45, C.accent4);
  const tx = MX + 6.5, tw = 12.1 - 6.5;
  stepRow(s, "A", "맨 위 스위치를 끕니다", "[사용 안 함]으로 바뀌어야 합니다. 이 기능 안에 'USB 케이블로 전달되는 명령 차단'이 들어 있습니다.", tx, 1.5, tw, C.accent4);
  stepRow(s, "B", "[자동으로 켜기]도 끕니다", "켜 두면 끈 뒤 30분이 지나 자동 차단이 다시 켜지고, 잘 되던 연결이 갑자기 끊깁니다.", tx, 3.0, tw, C.accent4);
  note(s, "작업 중에 휴대폰이 갑자기 목록에서 사라지면 대부분 이 기능이 다시 켜진 것입니다. 이 화면으로 돌아와 두 스위치를 확인하세요.", tx, 4.6, tw, 1.15, "warn");
}

// ================================================================== 3. 프로그램 사용하기
divider("03", "프로그램 사용하기", "실행부터 무음 적용, 빅스비 루틴 저장, 원래대로 되돌리기까지 순서대로 설명합니다.");
{
  const s = content("프로그램 실행하기");
  stepRow(s, 1, "GalaxyCameraMute.exe 더블클릭", "설치 과정 없이 바로 실행됩니다. 바탕화면이나 USB 메모리 등 원하는 폴더에 두고 쓰세요.", MX, 1.5, 6.4);
  stepRow(s, 2, "Windows 경고가 뜨면", "'Windows의 PC 보호' 창이 뜨면 [추가 정보] → [실행]을 누릅니다. 인터넷에서 받은 프로그램에 흔히 나오는 안내입니다.", MX, 2.85, 6.4);
  stepRow(s, 3, "ADB 도구 내려받기에서 [예]", "처음 한 번만 묻습니다. Google 공식 서버에서 약 10MB를 받아 exe와 같은 폴더의 platform-tools에 저장합니다.", MX, 4.2, 6.4);
  note(s, "ADB 도구는 Google이 배포하는 공식 도구이며, 프로그램에 포함하지 않고 사용자가 직접 Google에서 받는 방식입니다.", MX, 5.6, 6.4, 0.95, "info");
  const pic = picture(s, "app_06_download_box.png", { x: 7.55, y: 1.6, w: 5.15, name: "ADB 내려받기 확인 상자" });
  text(s, "처음 실행할 때 나오는 확인 상자. [예]를 누르면 내려받기가 시작되고, 상단 상태 표시줄에 진행률(%)이 표시됩니다.", { x: 7.55, y: pic.y + pic.h + 0.25, w: 5.15, h: 1.0, fontSize: 13, color: C.accent5 });
}
{
  const s = content("화면 구성");
  const pic = picture(s, "app_02_devices.png", { x: MX, y: 1.3, h: 5.6, name: "메인 화면" });
  const sc = pic.iw / pic.px;
  const marks = [
    [1, 468, 46], [2, 548, 46], [3, 612, 46], [4, 30, 133], [5, 587, 133], [6, 498, 190],
    [7, 330, 236], [8, 40, 661], [9, 390, 661], [10, 18, 690], [11, 22, 728],
  ];
  marks.forEach(([n, px, py]) => badge(s, n, pic.ix + px * sc - 0.17, pic.iy + py * sc - 0.17, 0.34));
  const legend = [
    ["설정 방법", "USB 디버깅 켜는 법을 사진으로 안내"],
    ["테마 전환", "버튼에 적힌 화면(다크/라이트)으로 바꾸기"],
    ["정보", "버전, 저작자, 오픈소스 라이선스"],
    ["상태 표시", "연결된 기기 수와 진행 상태"],
    ["새로고침", "기기 목록을 바로 다시 확인"],
    ["선택한 기기에만 적용", "켜면 고른 기기에만 적용"],
    ["기기 카드", "모델명, 시리얼, 연결·셔터음 상태"],
    ["카메라 무음 적용", "셔터음을 끄는 메인 버튼"],
    ["셔터음 원복", "셔터음을 다시 켜기"],
    ["빅스비 루틴도 추가", "무음 적용 때 루틴도 함께 (기본 켜짐)"],
    ["진행 상황 보기", "작업 기록(로그) 펼치기"],
  ];
  const lx = MX + pic.w + 0.5, lw = 12.1 - pic.w - 0.5;
  legend.forEach(([h, b], i) => {
    const y = 1.35 + i * 0.44;
    badge(s, i + 1, lx, y + 0.04, 0.34);
    s.addText([
      { text: h, options: { bold: true, color: C.text1 } },
      { text: "  " + b, options: { color: C.text2 } },
    ], { x: lx + 0.48, y, w: lw - 0.48, h: 0.42, fontSize: 14, valign: "middle", margin: 0, isTextBox: true });
  });
  note(s, "기기는 4초마다 자동으로 확인합니다. 케이블을 꽂으면 저절로 목록에 나타나고, 뽑으면 사라집니다.", lx, 6.3, lw, 0.6, "info");
}
{
  const s = content("기기 상태 읽는 법");
  const pic = picture(s, "app_01_empty.png", { x: MX, y: 1.35, h: 4.5, name: "기기 없음 화면" });
  text(s, "기기가 없을 때의 화면. [설정 방법 보기]를 누르면 휴대폰 준비 안내가 열립니다.", { x: MX, y: pic.y + pic.h + 0.15, w: pic.w, h: 0.75, fontSize: 13, color: C.accent5 });
  const tx = MX + pic.w + 0.5, tw = 12.1 - pic.w - 0.5;
  const rows = [
    [{ text: "표시", options: { bold: true, color: "FFFFFF", fill: { color: HEX.accent1 } } }, { text: "뜻과 할 일", options: { bold: true, color: "FFFFFF", fill: { color: HEX.accent1 } } }],
    [{ text: "연결됨", options: { bold: true, color: HEX.accent2 } }, "정상입니다. 바로 적용할 수 있습니다."],
    [{ text: "USB 디버깅 미승인", options: { bold: true, color: HEX.accent4 } }, "휴대폰의 허용 팝업에서 [허용]을 누르세요. (8단계)"],
    [{ text: "오프라인", options: { bold: true, color: HEX.accent4 } }, "케이블을 다시 꽂거나 USB 모드를 [파일 전송]으로 바꾸세요."],
    [{ text: "드라이버/권한 문제", options: { bold: true, color: HEX.accent4 } }, "USB 드라이버를 확인하고 PC를 재시작해 보세요."],
    [{ text: "무음", options: { bold: true, color: HEX.accent2 } }, "셔터음이 꺼진 상태입니다."],
    [{ text: "셔터음 켜짐", options: { bold: true, color: HEX.accent3 } }, "아직 적용 전이거나 원복한 상태입니다."],
    [{ text: "설정 없음(기본값)", options: { bold: true, color: HEX.accent5 } }, "설정값이 없는 기기입니다. 적용하면 '무음'이 됩니다."],
  ];
  s.addTable(rows, { x: tx, y: 1.4, w: tw, colW: [2.35, tw - 2.35], fontSize: 13, color: HEX.dk2, border: { type: "solid", pt: 0.75, color: "E2E4EC" }, fill: { color: "FFFFFF" }, rowH: 0.52, valign: "middle", margin: [0, 0.1, 0, 0.12] });
  note(s, "'알 수 없는 기기'는 인증 전이라 모델명을 읽지 못한 것입니다. 허용하면 모델명이 나타납니다.", tx, 5.85, tw, 0.75, "info");
}
{
  const s = content("카메라 무음 적용하기");
  const pic = picture(s, "app_04_muted.png", { x: 7.15, y: 1.3, h: 5.6, name: "무음 적용 완료 화면" });
  const w = 6.1;
  stepRow(s, 1, "기기가 [연결됨]인지 확인", "기기 카드에 초록색 [연결됨]이 보여야 합니다.", MX, 1.45, w);
  stepRow(s, 2, "[빅스비 루틴도 추가] 체크 확인", "기본으로 켜져 있습니다. 루틴이 필요 없으면 체크를 해제하세요.", MX, 2.65, w);
  stepRow(s, 3, "[카메라 무음 적용] 클릭", "연결된 모든 기기에 한 번에 적용하고, 값을 다시 읽어 제대로 바뀌었는지 확인합니다.", MX, 3.85, w);
  stepRow(s, 4, "[무음 적용 완료] 확인", "상태 표시가 초록색으로 바뀌고 기기 카드의 배지가 [무음]이 됩니다.", MX, 5.05, w);
  text(s, "오른쪽 화면은 [진행 상황 보기]를 펼친 모습입니다.", { x: MX, y: 6.4, w, h: 0.4, fontSize: 13, color: C.accent5 });
}
{
  const s = content("원하는 기기에만 적용하기");
  const pic = picture(s, "app_03_select.png", { x: MX, y: 1.3, h: 5.6, name: "기기 선택 화면" });
  const tx = MX + pic.w + 0.5, tw = 12.1 - pic.w - 0.5;
  stepRow(s, 1, "[선택한 기기에만 적용] 켜기", "목록 오른쪽 위의 체크박스를 켭니다. 기기 카드를 바로 눌러도 자동으로 켜집니다.", tx, 1.5, tw);
  stepRow(s, 2, "적용할 기기 카드 누르기", "선택된 카드는 보라색 테두리와 체크 표시가 생깁니다. 다시 누르면 선택이 풀립니다.", tx, 2.85, tw);
  stepRow(s, 3, "[카메라 무음 적용] 클릭", "선택한 기기에만 적용됩니다. 승인되지 않은 기기는 건너뛰고 기록에 남깁니다.", tx, 4.2, tw);
  note(s, "휴대폰 한 대만 쓴다면 이 기능은 필요 없습니다. 기본값은 연결된 모든 기기에 일괄 적용입니다.", tx, 5.6, tw, 0.85, "info");
}
{
  const s = content("빅스비 루틴 저장하기");
  const box = picture(s, "app_05_routine_box.png", { x: MX, y: 1.45, w: 4.6, name: "루틴 안내 상자" });
  text(s, "PC에 뜨는 안내 상자", { x: MX, y: box.y + box.h + 0.1, w: 4.6, h: 0.35, fontSize: 13, color: C.accent5 });
  stepRow(s, 1, "휴대폰 화면 확인", "무음 적용이 끝나면 휴대폰에 '카메라 무음' 루틴 화면이 자동으로 열립니다.", MX, 4.15, 4.7);
  stepRow(s, 2, "[저장] 누르기", "화면 아래의 [저장]을 눌러야 루틴이 추가됩니다. PC 상자는 [확인]으로 닫습니다.", MX, 5.45, 4.7);

  const ph = picture(s, "phone_routine.png", { x: 5.65, y: 1.3, h: 5.6, name: "휴대폰 루틴 화면" });
  const sc = ph.iw / ph.px;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: ph.ix + 640 * sc, y: ph.iy + 1865 * sc, w: 150 * sc, h: 170 * sc, rectRadius: 0.05, fill: { color: "FFFFFF", transparency: 100 }, line: { color: HEX.accent4, width: 2.5 }, objectName: "저장 버튼 강조" });
  badge(s, 2, ph.ix + 790 * sc, ph.iy + 1830 * sc, 0.4, C.accent4);

  const tx = 5.65 + ph.w + 0.45, tw = 12.7 - tx;
  s.addText("루틴 내용", { x: tx, y: 1.45, w: tw, h: 0.45, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
  const defs = [["언제", "카메라 앱을 실행할 때"], ["무엇을", "소리 모드를 무음으로"], ["끝나면", "루틴 실행 전 설정으로 돌아감"]];
  defs.forEach(([h, b], i) => {
    const y = 2.05 + i * 1.05;
    card(s, tx, y, tw, 0.9, C.background2, `routine-${i}`);
    s.addText(h, { x: tx + 0.2, y: y + 0.1, w: tw - 0.4, h: 0.32, fontSize: 13, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(b, { x: tx + 0.2, y: y + 0.44, w: tw - 0.4, h: 0.36, fontSize: 14, color: C.text1, margin: 0, isTextBox: true });
  });
  note(s, "화면이 안 뜨면 휴대폰 잠금을 풀어보세요. 그래도 안 되면 [내 파일 → 다운로드 → GalaxyCameraMute.rtn]을 직접 누르면 같은 화면이 열립니다.", tx, 5.3, tw, 1.55, "warn");
}
{
  const s = content("제대로 적용됐는지 확인하기");
  const steps = [
    ["카메라 앱 완전히 종료", "최근 앱 버튼(│││)을 눌러 카메라 앱을 위로 밀어 닫습니다. 열려 있던 카메라는 이전 설정을 기억할 수 있습니다."],
    ["카메라 다시 열기", "카메라를 다시 열면 빅스비 루틴이 실행되어 소리 모드가 무음으로 바뀝니다. (루틴을 저장한 경우)"],
    ["사진 한 장 찍어보기", "셔터음이 나지 않으면 성공입니다. 카메라를 닫으면 소리 모드는 원래대로 돌아옵니다."],
  ];
  steps.forEach(([h, b], i) => {
    const x = MX + i * 4.1;
    card(s, x, 1.5, 3.9, 3.6, C.background2, `check-${i}`);
    badge(s, i + 1, x + 0.3, 1.8, 0.6);
    s.addText(h, { x: x + 0.3, y: 2.6, w: 3.3, h: 0.5, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
    text(s, b, { x: x + 0.3, y: 3.2, w: 3.3, h: 1.75, fontSize: 14 });
    if (i < 2) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 3.88, y: 3.1, w: 0.24, h: 0.4, fill: { color: C.accent5 }, line: { color: C.accent5 }, objectName: `check-arrow-${i}` });
  });
  note(s, "그래도 소리가 나면 휴대폰을 한 번 재시작해 보세요. 프로그램에서 기기 배지가 [무음]인지도 확인하세요.", MX, 5.45, 12.1, 0.7, "info");
}
{
  const s = content("원래대로 되돌리기");
  const pic = picture(s, "app_07_unmuted.png", { x: 7.15, y: 1.3, h: 5.6, name: "셔터음 원복 화면" });
  const w = 6.1;
  s.addText("셔터음 다시 켜기", { x: MX, y: 1.4, w, h: 0.45, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true });
  stepRow(s, 1, "[셔터음 원복] 클릭", "설정값이 1로 돌아가고 기기 배지가 [셔터음 켜짐]으로 바뀝니다.", MX, 2.0, w);
  s.addText("빅스비 루틴 지우기 (휴대폰에서)", { x: MX, y: 3.4, w, h: 0.45, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true });
  stepRow(s, 2, "'모드 및 루틴' 앱 열기", "설정 → 모드 및 루틴 → [루틴] 탭으로 이동합니다.", MX, 4.0, w);
  stepRow(s, 3, "'카메라 무음' 루틴 삭제", "루틴을 선택해 삭제합니다. 원복 버튼은 루틴을 지우지 않습니다.", MX, 5.25, w);
}
{
  const s = content("설정 방법 창과 정보 창");
  const a = picture(s, "app_08_guide_1.png", { x: MX, y: 1.3, h: 4.75, name: "설정 방법 창" });
  const b = picture(s, "app_10_about.png", { x: MX + a.w + 0.4, y: 1.3, h: 4.75, name: "정보 창" });
  const tx = b.x + b.w + 0.45, tw = 12.7 - tx;
  s.addText("설정 방법 창", { x: tx, y: 1.4, w: tw, h: 0.42, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
  bullets(s, ["상단 [설정 방법] 버튼으로 엽니다", "1~8 번호나 [이전]/[다음], 키보드 ← → 로 이동", "승인 안 된 기기가 보이면 8단계가 자동으로 열립니다"], { x: tx, y: 1.9, w: tw, h: 1.9, fontSize: 14 });
  s.addText("정보 창", { x: tx, y: 4.0, w: tw, h: 0.42, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
  bullets(s, ["버전과 사용한 오픈소스 목록", "[라이선스 전문 보기]로 전체 라이선스 확인"], { x: tx, y: 4.5, w: tw, h: 1.4, fontSize: 14 });
  text(s, "왼쪽: 설정 방법 창(1단계)   오른쪽: 정보 창", { x: MX, y: 6.25, w: 8, h: 0.35, fontSize: 13, color: C.accent5 });
}

// ================================================================== 4. 문제 해결
divider("04", "문제 해결과 마무리", "자주 생기는 증상과 해결 방법, 사용 후 정리할 것을 모았습니다.");
{
  const s = content("문제 해결");
  const hdr = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: HEX.accent1 } } });
  const b = (t) => ({ text: t, options: { bold: true, color: HEX.dk1 } });
  const rows = [
    [hdr("증상"), hdr("확인할 것")],
    [b("USB 디버깅 스위치가 안 켜짐"), "보안 및 개인정보 보호 → 보안 위험 자동 차단 끄기 (+ [자동으로 켜기]도 끄기)"],
    [b("잘 되다가 갑자기 기기가 사라짐"), "자동 차단이 30분 뒤 다시 켜졌을 가능성이 큽니다. 다시 끄고 [자동으로 켜기]도 끄세요"],
    [b("목록이 비어 있음"), "케이블 연결과 USB 디버깅 확인. 충전 전용 케이블이 아닌지, USB 모드가 [파일 전송]인지 확인"],
    [b("USB 디버깅 미승인"), "휴대폰의 허용 팝업에서 [허용]. 팝업이 안 보이면 케이블을 다시 연결"],
    [b("오프라인"), "케이블 재연결, 또는 개발자 옵션 → [USB 디버깅 권한 승인 취소] 후 다시 연결"],
    [b("적용은 됐는데 소리가 남"), "카메라 앱을 완전히 종료한 뒤 다시 열기. 그래도 나면 휴대폰 재시작"],
    [b("루틴 화면이 안 뜸"), "휴대폰 잠금 해제. 안 되면 내 파일 → 다운로드 → GalaxyCameraMute.rtn 직접 열기"],
    [b("ADB 내려받기 실패"), "인터넷 연결 확인 후 프로그램 재실행. 회사망 등에서 막혔다면 다른 네트워크에서 시도"],
  ];
  s.addTable(rows, { x: MX, y: 1.35, w: 12.1, colW: [3.6, 8.5], fontSize: 13, color: HEX.dk2, border: { type: "solid", pt: 0.75, color: "E2E4EC" }, fill: { color: "FFFFFF" }, rowH: 0.58, valign: "middle", margin: [0, 0.1, 0, 0.15] });
}
{
  const s = content("사용 후 정리와 자주 묻는 질문");
  s.addText("사용 후 정리", { x: MX, y: 1.4, w: 5.6, h: 0.45, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true });
  stepRow(s, 1, "USB 디버깅 끄기", "설정 → 개발자 옵션 → USB 디버깅 끄기", MX, 2.0, 5.6, C.accent2);
  stepRow(s, 2, "개발자 옵션 끄기 (선택)", "개발자 옵션 맨 위 스위치를 끕니다", MX, 3.2, 5.6, C.accent2);
  stepRow(s, 3, "보안 위험 자동 차단 다시 켜기 (선택)", "다음에 다시 적용할 때는 또 꺼야 합니다", MX, 4.4, 5.6, C.accent2);
  note(s, "위 설정을 꺼도 셔터음 무음 설정과 빅스비 루틴은 그대로 유지됩니다.", MX, 5.75, 5.6, 0.75, "ok");

  const fx = 6.75, fw = 12.7 - fx;
  s.addText("자주 묻는 질문", { x: fx, y: 1.4, w: fw, h: 0.45, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true });
  const faq = [
    ["루팅이 필요한가요?", "아니요. 일반 설정값 하나만 바꿉니다."],
    ["업데이트 후 소리가 다시 나요", "One UI 업데이트로 초기화될 수 있습니다. 다시 적용하세요."],
    ["여러 대를 한 번에 할 수 있나요?", "네. 연결된 모든 기기에 한 번에 적용됩니다."],
    ["exe를 다른 PC로 옮겨도 되나요?", "네. 같은 폴더의 platform-tools도 함께 옮기면 다시 내려받지 않습니다."],
  ];
  faq.forEach(([q, a], i) => {
    const y = 2.0 + i * 1.18;
    card(s, fx, y, fw, 1.05, C.background2, `faq-${i}`);
    s.addText("Q. " + q, { x: fx + 0.25, y: y + 0.12, w: fw - 0.5, h: 0.38, fontSize: 15, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(a, { x: fx + 0.25, y: y + 0.52, w: fw - 0.5, h: 0.42, fontSize: 14, color: C.text2, margin: 0, isTextBox: true });
  });
}
{
  section = "문제 해결과 마무리";
  const s = pres.addSlide({ masterName: "COVER", sectionTitle: section });
  s.addText("이제 조용히 찍으세요", { placeholder: "title" });
  s.addText([
    { text: "막히면 프로그램의 [설정 방법] 버튼을 눌러 사진 안내를 다시 확인하세요.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "본인 소유 기기에만 사용하고, 타인을 동의 없이 촬영하지 마세요.", options: { color: "F2A7A7" } },
  ], { placeholder: "body" });
  picture(s, "phone_routine.png", { x: 9.0, y: 0.75, h: 6.0, name: "마무리 루틴 화면" });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  // 한글이 단어 중간에서 줄바꿈되지 않도록 텍스트 언어를 한국어로 지정
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(OUT));
  for (const name of Object.keys(zip.files)) {
    if (!/^ppt\/(slides|slideLayouts|slideMasters)\/[^/]+\.xml$/.test(name)) continue;
    const xml = await zip.file(name).async("string");
    zip.file(name, xml.replace(/lang="en-US"/g, 'lang="ko-KR" altLang="en-US"'));
  }
  fs.writeFileSync(OUT, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  await setTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
