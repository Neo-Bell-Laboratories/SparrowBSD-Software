"""Build a static information site and catalogs from official stable releases."""
import argparse, datetime, html, json, os, re, shutil, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO='Neo-Bell-Laboratories/SparrowBSD-Software'
GITHUB='https://github.com/'+REPO

def catalog(releases):
    result={'schema_version':1,'repository':GITHUB,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'releases':[],'os':[],'packages':[],'ports':[],'downloads':[],'remote_pkg_client_ready':False}
    for release in releases:
        if release.get('draft') or release.get('prerelease'):continue
        tag=release['tag_name'];url=release['html_url']
        if not url.startswith(GITHUB+'/releases/tag/'):raise ValueError('release URL is outside official repository')
        result['releases'].append({'tag':tag,'name':release.get('name') or tag,'url':url,'published_at':release.get('published_at')})
        for asset in release.get('assets',[]):
            download=asset['browser_download_url']
            if not download.startswith(GITHUB+'/releases/download/'):raise ValueError('asset URL is outside official repository')
            entry={'name':asset['name'],'url':download,'size':asset['size'],'digest':asset.get('digest'),'release':tag}
            result['downloads'].append(entry)
            name=entry['name'].lower()
            section='os' if name.startswith(('sparrowbsd-','os-')) else 'packages' if name.startswith('pkg-') else 'ports' if name.startswith('ports-') else None
            if section:result[section].append(entry)
    return result

def official_releases():
    releases=[];page=1
    while True:
        request=urllib.request.Request(f'https://api.github.com/repos/{REPO}/releases?per_page=100&page={page}',headers={'Accept':'application/vnd.github+json','User-Agent':'SparrowBSD-site'})
        token=os.environ.get('GH_TOKEN')
        if token:request.add_header('Authorization','Bearer '+token)
        with urllib.request.urlopen(request,timeout=30) as response:part=json.load(response)
        releases.extend(part)
        if len(part)<100:return releases
        page+=1

def build(releases,out):
    data=catalog(releases)
    if out.exists():shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(ROOT/'site/assets',out/'assets')
    (out/'catalog.json').write_text(json.dumps(data,indent=2)+'\n')
    template=(ROOT/'site/page.html').read_text()
    for page,title,kind in [('', 'SparrowBSD','home'),('pkg','Packages','packages'),('ports','Ports','ports'),('cdn','Downloads','downloads'),('docs','System notes','docs')]:
        base='../' if page else './'
        content=template.replace('{{BASE}}',base).replace('{{TITLE}}',title).replace('{{PAGE}}',kind)
        content=re.sub(r'<section\b[^>]*data-section="([^"]+)"[^>]*>.*?</section>',lambda m:m.group(0) if kind in m.group(1).split() else '',content,flags=re.S)
        latest='Latest stable release: '+data['releases'][0]['tag'] if data['releases'] else 'No official stable release has been published yet.'
        content=content.replace('Checking published releases…',html.escape(latest))
        channels={'packages':('PACKAGES','Native packages.','Artifacts published for the native SparrowBSD software channel.','The native pkg client currently installs trusted local source ports. This catalog does not enable remote package installation.'),'ports':('PORTS','Build from source.','Published source-port bundles for the native platform.','Remote bundles appear here after an official stable release publishes them.'),'downloads':('DOWNLOADS','From source to system.','System images and software assets from official stable releases.','Files are served directly from the official GitHub Releases. Check the target and checksum before use.')}
        if kind in channels:
            label,heading,description,notice=channels[kind]
            for ident,value in [('channel-name',label),('channel-title',heading),('channel-description',description),('channel-notice',notice)]:
                content=re.sub(r'(<[^>]*id="'+ident+r'"[^>]*>).*?(</[^>]+>)',lambda m:m.group(1)+html.escape(value)+m.group(2),content,count=1)
            rows=[]
            for asset in data[kind]:
                name,url,release,digest=[html.escape(str(asset.get(k) or 'Checksum not supplied')) for k in ['name','url','release','digest']]
                rows.append(f'<article class="artifact"><div><a href="{url}">{name} ↗</a><small>{release} · {digest}</small></div><span>{asset["size"]/1048576:.1f} MiB</span></article>')
            listing=''.join(rows) or '<p class="empty">No artifacts have been published in this channel yet. Official releases update this listing automatically.</p>'
            content=content.replace('<p>Loading the published catalog…</p>',listing)

        target=out/page;target.mkdir(exist_ok=True);(target/'index.html').write_text(content)
        if kind in ('packages','ports','downloads'):
            (target/'index.json').write_text(json.dumps({'schema_version':1,'repository':GITHUB,'generated_at':data['generated_at'],'remote_pkg_client_ready':False,'artifacts':data[kind]},indent=2)+'\n')
    (out/'.nojekyll').touch()
    (out/'404.html').write_text('<!doctype html><meta charset="utf-8"><title>Not found · SparrowBSD</title><h1>Page not found</h1><p>Return to <a href="https://sparrowbsd.com">SparrowBSD</a>.</p>')
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--releases',type=Path);parser.add_argument('--out',type=Path,default=ROOT/'dist');args=parser.parse_args()
    releases=json.loads(args.releases.read_text()) if args.releases else official_releases()
    data=build(releases,args.out)
    print(f"Built {len(data['releases'])} official releases and {len(data['downloads'])} artifacts")
