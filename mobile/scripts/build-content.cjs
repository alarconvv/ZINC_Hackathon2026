const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../content');
fs.writeFileSync(path.join(root,'legal.json'),JSON.stringify({privacy:fs.readFileSync(path.join(root,'privacy.md'),'utf8'),terms:fs.readFileSync(path.join(root,'terms.md'),'utf8')},null,2)+'\n');
