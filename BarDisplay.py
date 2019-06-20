from IPython.display import display, HTML, Javascript

class BarDisplay():
    def __init__(self, idlist):
        self.progressTracker = {
            bar_id : 0
            for bar_id in idlist
        }
        self.html_template = """
        <style>
            #myProgress{BAR_ID} {
                width: 100%;
                background-color: #ddd;
            }
        </style>
        <style>
            #myBar{BAR_ID} {
                width: 0%;
                height: 30px;
                background-color: #4CAF50;
                text-align: center;
                line-height: 30px;
                color: white;
            }
        </style>
        <h1 id="myHeader{BAR_ID}">Job #{BAR_ID}</h1>
        <div id="myProgress{BAR_ID}">
            <div id="myBar{BAR_ID}">0%</div>
        </div>
        <script>
            function checkTime(i) {
                if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
                return i;
            }

            var progress{BAR_ID} = 0;
            var tstart{BAR_ID} = new Date();
            tstart{BAR_ID} = tstart{BAR_ID}.getTime();

            (function timer{BAR_ID}() {
            if (progress{BAR_ID} < 100){
                var segment = new Date();
                segment = segment.getTime() - tstart{BAR_ID};
                var m = Math.floor(segment / 60000);
                var s = Math.floor((segment % 60000) / 1000);
                m = checkTime(m);
                s = checkTime(s);
                document.getElementById('myHeader{BAR_ID}').innerHTML = "Job #{BAR_ID} (" + m + ":" + s + ")";

                var t = setTimeout(timer{BAR_ID}, 1000 - segment % 1000);
            }
            })();
        </script>
        """
        self.js_update_bar = """
        progress{BAR_ID} = progress{BAR_ID} + {ADD_PROGRESS};
        if (progress{BAR_ID} > 100) progress{BAR_ID} = 100;
        var elem = document.getElementById("myBar{BAR_ID}");
        elem.style.width = progress{BAR_ID} + '%'; 
        elem.innerHTML = progress{BAR_ID} * 1  + '%';
        """
    def show(self):
        for bar_id in self.progressTracker.keys():
            display(HTML(self.html_template.replace('{BAR_ID}', str(bar_id))))
    def update(self, bar_id, progress):
        if bar_id in self.progressTracker:
            self.progressTracker[bar_id] += progress
            if self.progressTracker[bar_id] >= 100:
                self.progressTracker.pop(bar_id)
            display(Javascript(self.js_update_bar.replace('{ADD_PROGRESS}', str(progress)).replace('{BAR_ID}', str(bar_id))))
    def isDone(self):
        return not len(self.progressTracker.keys()) 
