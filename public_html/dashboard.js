function openNav() {
    document.getElementById("sidenav").style.width = "250px";
}

function closeNav() {
    document.getElementById("sidenav").style.width = "0";
}

document.addEventListener("DOMContentLoaded", () => {

    // Live dashboard update
    async function updatedashboard() {
        try {
            const res = await fetch('sensor.json', { cache: 'no-store' });
            const data = await res.json();

            document.getElementById("temp").innerText = data.TempF + " °F | " + data.TempC + " °C";
            document.getElementById("humidity").innerText = data.Humidity + "%";
            document.getElementById("time").innerText = "Time: " + data.Time;

            document.getElementById("maxtemp").innerText = data.MaxTempF + " °F";
            document.getElementById("maxtemptime").innerText = data.MaxTempTime;

            document.getElementById("mintemp").innerText = data.MinTempF + " °F";
            document.getElementById("mintemptime").innerText = data.MinTempTime;

            document.getElementById("maxhumidity").innerText = data.MaxHumidity + "%";
            document.getElementById("maxhumiditytime").innerText = data.MaxHumidityTime;

            document.getElementById("minhumidity").innerText = data.MinHumidity + "% ";
            document.getElementById("minhumiditytime").innerText = data.MinHumidityTime;

        } catch (err) {
            console.error("Failed to fetch sensor.json:", err);
        }
    }

    // Graph functions
    async function loadDayGraph() {
        const res = await fetch("graph.php?range=day");
        const data = await res.json();

        data.times = data.times.map(t => t.trim());

        console.log("Day graph cleaned data:", data);

        if (!data.times.length || !data.temps.length) {
            document.getElementById("dayPlot").innerText = "No data available for today";
            return;
        }

        Plotly.newPlot("dayPlot", [{
            x: data.times,
            y: data.temps,
            mode: "lines+markers"
        }], {
            title: "Today's Temperature",
            xaxis: { title: "Time" },
            yaxis: { title: "Temp (°F)" }
        });
    }
    async function loadMonthGraph() {

        const res = await fetch("graph.php?range=month");
        const data = await res.json();

        Plotly.newPlot("monthPlot", [{
            x: data.times,
            y: data.temps,
            mode: "lines+markers"
        }], {
            title: "Monthly Temperature",
            xaxis: { title: "Date" },
            yaxis: { title: "Temp (°F)" }
        });

    }
    // Calandar
    async function loadDayGraphForDate(dateStr) {
        const res = await fetch(`graph.php?range=day&date=${dateStr}`);
        const data = await res.json();

        if (!data.times.length) {
            document.getElementById("calendarplot").innerText = "no data for this day";
            return;
        }


        Plotly.newPlot("calendarplot", [{
            x: data.times,
            y: data.temps,
            mode: "lines+markers"
        }], {
            title: `Temperature for ${dateStr}`,
            xaxis: { title: "Time" },
            yaxis: { title: "Temp (°F)" }
        });

    }




    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        dateClick : function(info) {
            console.log("Clicked date:", info.dateStr);

            loadDayGraphForDate(info.dateStr);
        }
    });
    calendar.render();


    // Start updates
    updatedashboard();
    loadDayGraph();
    loadMonthGraph();

    setInterval(updatedashboard, 30000);
    setInterval(loadDayGraph, 30000);
});
