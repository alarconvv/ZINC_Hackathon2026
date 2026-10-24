const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../content');
const documents=path.resolve(__dirname,'../..');
fs.writeFileSync(path.join(root,'legal.json'),JSON.stringify({privacy:fs.readFileSync(path.join(documents,'privacy.md'),'utf8'),terms:fs.readFileSync(path.join(documents,'terms.md'),'utf8')},null,2)+'\n');
