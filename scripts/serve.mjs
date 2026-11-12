import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
export const defaultRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../dist');
export function normalizePrefix(value='') {
 const prefix=String(value).replace(/\/$/,'');
 if(prefix&&!/^\/(?:[A-Za-z0-9_-]+\/)*[A-Za-z0-9_-]+$/.test(prefix))throw new Error('Invalid BASE_PATH');
 return prefix;
}
export function createStaticServer({root=defaultRoot,prefix=''}={}) {
 root=fs.realpathSync(root);prefix=normalizePrefix(prefix);
 const inside=file=>file===root||file.startsWith(root+path.sep);
 const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.jpg':'image/jpeg','.txt':'text/plain; charset=utf-8','.md':'text/markdown; charset=utf-8'};
 return http.createServer((req,res)=>{
  function send(file,status=200){res.writeHead(status,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Content-Length':fs.statSync(file).size,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});if(req.method==='HEAD')return res.end();const stream=fs.createReadStream(file);stream.on('error',()=>res.destroy());stream.pipe(res);}
  function notFound(){const file=path.join(root,'404.html');if(fs.existsSync(file))return send(file,404);res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'});res.end(req.method==='HEAD'?'':'404 — IRO page not found');}
  try{
   if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{'Allow':'GET, HEAD'});return res.end('Method not allowed');}
   const url=new URL(req.url,'http://localhost');let request=decodeURIComponent(url.pathname);
   if(request.includes('\0')||request.includes('\\')){res.writeHead(400);return res.end('Bad path');}
   if(prefix){if(request===prefix){res.writeHead(301,{Location:prefix+'/'+url.search});return res.end();}if(!request.startsWith(prefix+'/'))return notFound();request=request.slice(prefix.length);}
   let file=path.resolve(root,'.'+request);if(!inside(file)){res.writeHead(403);return res.end('Forbidden');}
   if(!fs.existsSync(file))return notFound();
   file=fs.realpathSync(file);if(!inside(file)){res.writeHead(403);return res.end('Forbidden');}
   if(fs.statSync(file).isDirectory()){if(!url.pathname.endsWith('/')){res.writeHead(301,{Location:url.pathname+'/'+url.search});return res.end();}file=path.join(file,'index.html');}
   if(!fs.existsSync(file)||!fs.statSync(file).isFile())return notFound();
   return send(file);
  }catch{res.writeHead(400);res.end('Bad request');}
 });
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 if(!fs.existsSync(defaultRoot))throw new Error('Run npm run build first.');
 const port=Number(process.env.PORT||4173);if(!Number.isInteger(port)||port<1||port>65535)throw new Error('Invalid port');
 const prefix=normalizePrefix(process.env.BASE_PATH||'');
 createStaticServer({prefix}).listen(port,'127.0.0.1',()=>console.log(`IRO local preview: http://127.0.0.1:${port}${prefix}/`));
}
