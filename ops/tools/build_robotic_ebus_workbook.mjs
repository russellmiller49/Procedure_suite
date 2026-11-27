import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {parseArgs} from 'node:util';
const root=fileURLToPath(new URL('../../',import.meta.url));
const {values:args}=parseArgs({options:{
  dictionary:{type:'string',default:path.join(root,'data/knowledge/robotic_ebus_v1/launch_dictionary.json')},
  output:{type:'string',default:path.join(root,'outputs/robotic_ebus_v1/Robotic_EBUS_Launch_Dictionary_0_2_0.xlsx')},
  runtime:{type:'string',default:process.cwd()}
}});
const require=createRequire(path.join(path.resolve(args.runtime),'artifact-loader.cjs'));
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const output=path.resolve(args.output),outputDir=path.dirname(output);
await fs.mkdir(outputDir,{recursive:true});

const input = JSON.parse(await fs.readFile(args.dictionary, 'utf8'));
const wb = Workbook.create();
const launch = wb.worksheets.add('Launch fields');
const roadmap = wb.worksheets.add('Roadmap');
const headers = ['Contract field', 'Dictionary reference', 'Definition', 'Values / units', 'Required when', 'Preferred source', 'Missingness', 'National destination', 'Mapping', 'Review notes'];
const rows = input.fields.map(r => [r.contract_path, r.dictionary_key ? `${r.dictionary_key} (row ${r.source_row})` : 'Implementation extension', r.definition, r.contract_units || r.source_allowed_values_units || JSON.stringify(r.contract_schema), r.required_when || 'When applicable', r.preferred_source || 'System', r.missingness_policy, r.national_destination || 'Hospital only', r.mapping, '']);
const bindings = input.context_bindings.map(r => [r.contract_path, `${r.dictionary_key} (row ${r.source_row})`, r.definition, 'Validated context / system linkage', 'All cases', 'Authenticated patient and encounter context', 'Required context', r.national_destination || 'Hospital only', 'context binding', '']);
rows.push(...bindings);
launch.getRange('A2').values = [['Robotic bronchoscopy and linear EBUS — launch dictionary']];
launch.getRange('A3').values = [[`Contract ${input.schema_version}. Source: ${input.source_workbook}, Data_Dictionary. Original workbook is unchanged.`]];
launch.getRange('A4').values = [['Launch fields and context bindings']];
launch.getRange('B4').formulas = [[`=COUNTA(A7:A${6+rows.length})`]];
launch.getRange('A5').values = [['Blank clinical values retain a missingness reason. National fields remain subject to the approved release profile.']];
launch.getRange('A6:J6').values = [headers];
launch.getRange(`A7:J${6+rows.length}`).values = rows;
launch.getRange('A:A').format.columnWidth = 46;
launch.getRange('B:B').format.columnWidth = 46;
launch.getRange('C:C').format.columnWidth = 65;
launch.getRange('D:D').format.columnWidth = 50;
launch.getRange('E:G').format.columnWidth = 47;
launch.getRange('H:H').format.columnWidth = 44;
launch.getRange('I:J').format.columnWidth = 24;
launch.getRange(`A7:J${6+rows.length}`).format.wrapText = true;
launch.getRange(`A7:J${6+rows.length}`).format.rowHeight = 100;
launch.getRange(`J7:J${6+rows.length}`).format.fill = '#FFF4CC';
launch.getRange('A2').format.font = {size:16,bold:true};
launch.getRange('A3:J5').format.rowHeight = 22;
launch.freezePanes.freezeRows(6);
launch.freezePanes.freezeColumns(1);

const roadmapHeaders = ['Dictionary field', 'Field label', 'Tier', 'Data type', 'Values / units', 'Definition', 'Required when', 'Preferred source', 'Missingness', 'Source row'];
const future = input.roadmap.map(r => [r.dictionary_key, r['Field label'], r['Collection tier'], r['Data type'], r['Allowed values / units'], r['Definition / capture instruction'], r['Required when'], r['Preferred source'], r['Missingness policy'], r.source_row]);
roadmap.getRange('A2').values = [['Fields retained for later phases']];
roadmap.getRange('A3').values = [[`Source: ${input.source_workbook}, Data_Dictionary. Remaining source fields are retained for later phases or alternative representations.`]];
roadmap.getRange('A4').values = [['Deferred source fields']];
roadmap.getRange('B4').formulas = [[`=COUNTA(A7:A${6+future.length})`]];
roadmap.getRange('A6:J6').values = [roadmapHeaders];
roadmap.getRange(`A7:J${6+future.length}`).values = future;
roadmap.getRange('A:B').format.columnWidth = 44;
roadmap.getRange('C:D').format.columnWidth = 18;
roadmap.getRange('E:I').format.columnWidth = 54;
roadmap.getRange('J:J').format.columnWidth = 14;
roadmap.getRange(`A7:J${6+future.length}`).format.wrapText = true;
roadmap.getRange(`A7:J${6+future.length}`).format.rowHeight = 96;
roadmap.getRange('A2').format.font = {size:16,bold:true};
roadmap.freezePanes.freezeRows(6);
roadmap.freezePanes.freezeColumns(1);
for (const s of [launch,roadmap]) {
  s.showGridLines = false;
  s.getRange('A2:J2').format.rowHeight = 32;
  s.getUsedRange().format.font.name = 'Arial';
  s.getRange(`A6:J${s===launch?6+rows.length:6+future.length}`).format.font.size = 11;
  s.getRange('A6:J6').format = {fill:'#163A4A',font:{bold:true,color:'#FFFFFF',name:'Arial',size:11},wrapText:true,rowHeight:36};
  s.getUsedRange().format.verticalAlignment = 'top';
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Launch fields!A4:B4',include:'values,formulas',tableMaxRows:1,tableMaxCols:2})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},summary:'formula errors'})).ndjson);
for (const name of ['Launch fields','Roadmap']) {
  const png = await wb.render({sheetName:name,range:'A1:D10',scale:1,format:'png'});
  await fs.writeFile(path.join(outputDir,`${name.replace(' ','_')}.png`), new Uint8Array(await png.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(output);
