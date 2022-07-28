<h1 align="center">
    <b>
        sv-dlp
    </b>
</h1>

sv-dlp is a panorama scraper for various street view platforms that can download, 
obtain metadata and short URLs.

sv-dlp heavily relies on reverse engineered APIs - in the event of one service
not working, please submit an issue with the `Dead API` label 
and will be solved as soon as possible once I (or a collaborator)

This project has been made for educational purposes and all content scraped from
is owned by their respective authors.

sees it.

## **Features**
- Download Panoramas
    - A panorama ID, a coordinate or a short URL can be parsed
        - **[GOOGLE]** A can radius can be parsed as well 
    - Is multithreaded, meaning that each row is being downloaded at the same time enhancing speed
    - Saves individual tiles if `--save-tiles` is parsed
    - Download from .csv/.json input obtained from [Nur's Map Generator](https://map-generator-flax.vercel.app/)
- Fully print metadata
    - Date and coords can also be printed too separately
- Coordinates and short URLs are automatically turned to panorama IDs
- Short links with a panorama ID (or coordinates aswell)

A built-in generator is also planned for intensive tasks that the web browser version cannot perform well due to JavaScript's inefficiency.

## **Services**
Service|Status|Notes
:------|:-----|:----
Google |100%  |Zoom 5 only obtains a portion of the face, but that might be Google's problem.
Yandex |99%   |Short Link function does not use the `shortenPath` API call. Only crops panorama for one specific resolution.
Bing   |95%   |Misc features not implemented; only obtains metadata by coords
Baidu  |33%   |**Is in own branch**; metadata and misc features partially implemented; does not get all zooms and faces correctly
Apple  |15%   |Can only scrape with Panorama ID; metadata and misc features not implemented

## **Installation**
### **Windows**
[W.I.P]
### **Linux**
[W.I.P]

## **FAQ**
## **Is this in a pre-release state?**
For now, yes. Until all services reach a 95% state (except Baidu due to its own branch) and the UX is considered good by my standards, sv-dlp will stay as a pre-release.
## **Why aren't all my coordinates from .csv downloading?**
Depending on how close the given coordinates are, it'll download the same panorama ID no matter the difference. It's recommended to use .json or .csv with panorama IDs instead.
## **Can X Service be added?**
Depending on how accesible it is scraping-wise, yes.
**Feel free to submit in an issue** about the specific service and I'll gladly see what I can do about it. If you're a developer though, refer to the next question.
## **I'm a developer and I want to add X service or improve the code. Can I?**
Sure! You're welcome to submit in a pull request as long as its to improve
this program, such as improving performance, fixing a bug, adding a service, etc.
For those who want to add a service, check out [the documentation for it](https://github.com/juanpisuribe13/sv-dlp/blob/master/extractor/README.md).
## **What does sv-dlp stand for?**
~~IDK i copied it from yt-dlp since I got inspiration from it~~ Street View Download Plus; sv-dlp is more than a downloader if you look at its features.

## **License**
[MIT](https://raw.githubusercontent.com/juanpisuribe13/sv-dlp/master/LICENSE)
