// pptx 의 테마 색(clrScheme)과 테마 이름을 바꾼다.
// pptxgenjs 는 글꼴만 테마에 넣고 색은 Office 기본값으로 두기 때문에, 저장 후 이 함수로 덮어쓴다.
//
//   const { setTheme } = require("./set_theme");
//   await setTheme("deck.pptx", { name: "...", colors: { dk1, lt1, dk2, lt2, accent1..6, hlink, folHlink } });
const fs = require("fs");

// jszip 은 pptxgenjs 의 의존성으로 함께 설치된다
const JSZip = require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));

const ORDER = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4",
  "accent5", "accent6", "hlink", "folHlink"];

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

async function setTheme(file, theme) {
  for (const key of ORDER) {
    if (!/^[0-9A-Fa-f]{6}$/.test(theme.colors[key] || "")) throw new Error(`색 ${key} 가 6자리 hex 가 아님`);
  }
  const name = esc(theme.name);
  const scheme = `<a:clrScheme name="${name}">` +
    ORDER.map((k) => `<a:${k}><a:srgbClr val="${theme.colors[k].toUpperCase()}"/></a:${k}>`).join("") +
    `</a:clrScheme>`;

  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const parts = Object.keys(zip.files).filter((p) => /^ppt\/theme\/theme\d+\.xml$/.test(p));
  for (const p of parts) {
    let xml = await zip.file(p).async("string");
    xml = xml.replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, scheme);
    xml = xml.replace(/(<a:theme\b[^>]*\bname=")[^"]*(")/, `$1${name}$2`);
    zip.file(p, xml);
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

module.exports = { setTheme };
