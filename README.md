<h1 align="center">
    <b>
        sv-dlp
    </b>
</h1>

sv-dlp is a panorama scraper for various street view platforms.


This project has been made for educational purposes and all content scraped from
is owned by their respective authors.

## **Features**
- Download Panoramas
    - A panorama ID, a coordinate or a short URL can be parsed.
    - Is multithreaded, meaning that every row is being downloaded at the same time enhancing speed.
    - Saves individual tiles if `--save-tiles` is parsed.
    - Download from .csv/.json input obtained from [Nur's Map Generator](https://map-generator-flax.vercel.app/)
- Fully print metadata
    - Date and coords can also be printed too separately.
- Coordinates and short URLs are automatically turned to panorama IDs

A built-in generator is also planned for intensive tasks that the web browser version cannot perform well due to JavaScript's inefficiency.

## **Services**
Service|Status|Notes
:------|:-----|:----
Google |100%  |Highest zoom only obtains a portion of the face, but that might be Google's problem.
Yandex |91%   |Misc features semi-implemented
Bing   |50%   |Metadata and misc feaures not implemented; [stiching tiles is borked](https://cdn.discordapp.com/attachments/757702072614518905/954514968064196628/0301001312233013.png)
Baidu  |33%   |**Is in own branch**; metadata and misc features partially implemented; does not get all zooms and faces correctly

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
## **I'm a develper and I want to add X service or improve the code. Can I?**
Sure! You're welcome to submit in a pull request as long as its to improve
this program, such as improving performance, fixing a bug, adding a service, etc.

For those who want to add a service, check out [the documentation for it](https://github.com/juanpisuribe13/sv-dlp/blob/master/extractor/README.md).

## **License**
[MIT](https://raw.githubusercontent.com/juanpisuribe13/sv-dlp/master/LICENSE)