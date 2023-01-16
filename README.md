<h1 align="center">
    <b>
        sv-dlp 
    </b>
</h1>

sv-dlp is a panorama scraper for various street view platforms that can download, 
obtain metadata and short URLs.

sv-dlp heavily relies on reverse engineered APIs - in the event of one service
not working, please submit an issue with the `Dead API` label 
and will be solved as soon as possible once I (or a collaborator) sees it.

This project has been made for educational purposes and all content scraped from
is owned by their respective authors.

## **Features**
- Download Panoramas
    - A panorama ID, a coordinate or a short URL can be parsed
        - **[Google]** Radius can be parsed if input is coordinates 
    - Is multithreaded; each panorama tile row is in different threads for faster downloads
    - Saves individual tiles if `--save-tiles` is parsed
    - Download from .csv/.json files
- Fully print metadata
    - Coords, Date, Panorama ID and Gen can be printed separately
- Coordinates and short URLs are automatically turned to Panorama IDs
- Short links with a Panorama ID or coordinates

## **Services**
Service|Status|Notes
:------|:-----|:----
Google |100%  |Zoom 5 only obtains a portion of the face, but that might be Google's problem.
Baidu  |99%   |Downloading might be slow depending on how far you are from Baidu's servers; translation between BD09MC and WGS84 is innacurate
Yandex |99%   |Short Link function does not use the `shortenPath` API call.
Apple  |95%   |Misc features not supported; can only obtain metadata by coords - credit to [sk-zk & retroplasma](https://github.com/juanpisss/sv-dlp/blob/master/CREDITS)
Bing   |95%   |Misc features not implemented; can only obtain metadata by coords - credit to [sk-zk](https://github.com/juanpisss/sv-dlp/blob/master/CREDITS)

## **Installation**
### Automatic
```bash
$ python3 -m pip install sv-dlp
$ python3 -m sv_dlp
```
### Manual
If you prefer using a binary instead, check out the binaries [here](https://github.com/juanpisss/sv-dlp/releases/latest)
and add them to your `PATH` folder. Check out this [guide](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
for more information.

## **FAQ**
### **Why aren't all my coordinates from .csv downloading?**
Depending on how close the given coordinates are, it'll download the same panorama ID no matter the difference. It's recommended to use .json or .csv with panorama IDs instead.
## **Can X Service be added?**
Depending on how accesible it is scraping-wise, yes.
**Feel free to submit in an issue** about the specific service and I'll gladly see what I can do about it. If you're a developer though, refer to the next question.
### **I'm a developer and I want to add X service or improve the code. Can I?**
Sure! You're welcome to submit in a pull request as long as its to improve
this program, such as improving performance, fixing a bug, adding a service, etc.
For those who want to add a service, check out [the documentation for it](https://juanpisss.github.io/sv-dlp/contributing_services/).

## **License**
[MIT](https://raw.githubusercontent.com/juanpisss/sv-dlp/master/LICENSE)
