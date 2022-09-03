# Downloading Process
sv_dlp first builds a Tile URL array, where each column and row
represents its x and y position respectfully on the panorama, such as the one shown below.

![Column/Row Array - Credit to GeeksforGeeks](https://media.geeksforgeeks.org/wp-content/uploads/two-d.png)

After building the array, a `ThreadPoolExecutor` object is called; threads are generated 
based on the length of the y axis; each thread downloads its respectful row and stores it
into a Tile IO array with its respectful axis position.

Once the downloading process is complete, all rows get stitched separately, then all columns
are merged into one single image.

# Benefit of using MultiThreading
Time.

If downloading a panorama with a lower zoom level, difference isn't that much, but
within my findings downloading larger zoom levels take huge amounts of seconds.

Approximately there's a difference of 45 seconds when downloading a panorama with 
zoom of level 5 with MultiThreading and WITHOUT multithreading.

# Conclusions
Sure, there's some room for improvement for the downloader, but I'm really 
proud of the way it turned out. From the speed to the user experience, I find it 
good enough for my standards. If you don't, then feel welcome to submit a pull request
with changes that may benefit the end-user - I'll gladly check it out.