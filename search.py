import requests, bs4, re, time

def get_latest_plugin_list():
    plugin_list_html = requests.get('http://plugins.svn.wordpress.org/')
    plugin_list_html.raise_for_status()
    plugin_list_parsed = bs4.BeautifulSoup(plugin_list_html.text)
    plugin_names=plugin_list_parsed.select("li")
    plugin_list=[]
    for i,plugin in enumerate(plugin_names):
        name=plugin_names[i].getText()[:-1]
        if ("\\" in r"%r" % name):
            pass
        else:
            plugin_list.append(name)
    return plugin_list

def get_plugin_page_soup(title):
    url='https://wordpress.org/plugins/'+title
    plugin_page_soup = requests.get(url)
    plugin_page_soup.raise_for_status()
    return bs4.BeautifulSoup(plugin_page_soup.text, "html.parser")


def get_details(search_term,soup):
    details = soup.find_all(text=re.compile(search_term))
    for item in details:
        nextSib = item.nextSibling
        return nextSib

def get_plugin_summary_row(plugin_title):
    soup=get_plugin_page_soup(plugin_title)
    
    #Title & URL
    value = soup.select('h1[class="plugin-title"]')
    tr= "<tr><td><a href='" + str(value[0].select('a')[0].attrs['href']) + "'>" + str(value[0].getText()) + "</a></td>"
    
    # tags
    value = get_details("Tags:",soup)
    all_tags=value.select('a')
    tags=[]
    for tag in all_tags:
        tags.append(tag.getText())
    taglist = " ".join( str(x) for x in tags)
    tr = tr + "<td>" + taglist + "</td>"
    
    #Version:
    #value = get_details("Version:",soup)
    #print "Plugin version: " + str(value.getText())
    
    #Last updated NEED TO GET DATE ONLY
    value = get_details("Last updated:",soup)
    last_updated=value.select('span')[0].attrs['content']
    tr = tr + "<td>" + str(last_updated) + "</td>"
    
    #Active installs
    value = get_details("Active installs:",soup)
    active_installs = value.getText()
    active_installs = re.sub('[+,]', '', active_installs) #removes + and commas
    active_installs=int(re.search(r'\d+', active_installs).group()) # remvoes less than
    tr = tr + "<td>" + str(active_installs) + "</td>"
    
    #Tested up to:
    value = get_details("Tested up to:",soup)
    tr = tr + "<td>" + str(value.getText()) + "</td>"
    
    #rating
    #div = soup.select('div[class="wporg-ratings"]')
    rating= soup.select('meta[itemprop="ratingValue"]')
    if (rating != []):
        tr = tr + "<td>" + str(rating[0].attrs['content']) + "</td>"
    else:
        tr = tr + "<td>" + str("0") + "</td>"
    
    tr = tr + "</tr>"
    return tr
    
    
    
def output_html(plugin_list):
    
    header="""
    <html>
    <head>

<style>
h1 {
    font-family: verdana;
    font-size: 200%;
}

</style>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.13/css/jquery.dataTables.css">
    
  
<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.13/js/jquery.dataTables.js"></script>
<script type="text/javascript">
$(document).ready( function () {
    $('#table_id').DataTable();
} );
</script>

<script id="mNCC" language="javascript">
   medianet_width = "728";
   medianet_height = "90";
   medianet_crid = "313262820";
   medianet_versionId = "111299";
   (function() {
       var isSSL = 'https:' == document.location.protocol;
       var mnSrc = (isSSL ? 'https:' : 'http:') + '//contextual.media.net/nmedianet.js?cid=8CU1VN24B' + (isSSL ? '&https=1' : '');
       document.write('<scr' + 'ipt type="text/javascript" id="mNSC" src="' + mnSrc + '"></scr' + 'ipt>');
   })();
</script>

</head>
    <body>


<h1>
    <a href="http://andypi.co.uk/2017/04/08/wordpress-plugins-advanced-search/">AndyPi's WordPress Plugins Search</a>
</h1>

<h2>
This list last updated: """ + time.strftime("%A %d %B %Y") +  """<br>
</h2>
<p>
Shift-click on a column to add a secondary sort
</p>

<div>
<table id="table_id" style="margin-left:auto;margin-right:auto">
    <thead>
        <tr>
            <th>Plugin Title</th>
            <th>Tags</th>
            <th>Last updated</th>
            <th>Active installs</th>
            <th>Tested upto WP version</th>
            <th>Rating</th>
        </tr>
    </thead>
    <tbody>"""
    
    with open("index.html", "w+") as myfile:
        myfile.write(header)
    
    for plugin_title in plugin_list:
        try:
            tr=get_plugin_summary_row(plugin_title)
            with open("index.html", "a") as myfile:
                myfile.write(tr)
            print plugin_title
        except:
            pass
        
    print "Finished"

plugin_list=get_latest_plugin_list()
output_html(plugin_list)

#https://datatables.net/
