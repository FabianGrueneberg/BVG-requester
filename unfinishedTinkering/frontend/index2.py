import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

# Simulated data: Arrival times of buses
arrival_times = np.random.normal(loc=0, scale=1, size=1000)  # Normal distribution

# Calculate statistics
mean = np.mean(arrival_times)
std_dev = np.std(arrival_times)
three_sigma = 3 * std_dev

# Create histogram plot using Plotly
fig = go.Figure(data=[go.Histogram(x=arrival_times, nbinsx=30, opacity=0.75)])
fig.update_layout(
    title="",  # Removed the plot header
    xaxis_title="Arrival Time",
    yaxis_title="Frequency",
    template="plotly_white",
    autosize=True,
    height=None,  # Let the CSS control the height
)

# Generate the HTML snippet for the plot
plot_html = pio.to_html(fig, full_html=False)

# HTML content with embedded plot and statistics
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bus Arrival Times at Reuchlinstr.</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 5px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 1000px;
            text-align: center;
        }}
        h1 {{
            color: #333;
        }}
        #plot {{
            width: 100%;
            max-width: 700px;
            margin: 0 auto;
            height: auto;
            aspect-ratio: 4 / 3;  /* Normal aspect ratio is 4:3 */
        }}
        @media (max-width: 600px) {{
            #plot {{
                aspect-ratio: 1 / 1;  /* For small screens, make it square */
            }}
        }}
        .statistics {{
            margin: 20px 0;
            font-size: 18px;
            text-align: center;  /* Center the statistics */
        }}
        .textbox {{
            margin-top: 30px;
            padding: 15px;
            background: #eee;
            border-radius: 5px;
            font-size: 16px;
            line-height: 1.6;
            text-align: left;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Arrivaltimes of Busses at Reuchlinstr.</h1>
        <div id="plot">
            {plot_html}
        </div>
        <div class="statistics">
            <p><strong>Mean:</strong> {mean:.2f}</p>
            <p><strong>Standard Deviation:</strong> {std_dev:.2f}</p>
            <p><strong>3-Sigma Value:</strong> {three_sigma:.2f}</p>
        </div>
        <div class="textbox">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus imperdiet, nulla et dictum interdum, nisi lorem egestas odio, vitae scelerisque enim ligula venenatis dolor. Maecenas nisl est, ultrices nec congue eget, auctor vitae massa. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus imperdiet, nulla et dictum interdum, nisi lorem egestas odio, vitae scelerisque enim ligula venenatis dolor. Maecenas nisl est, ultrices nec congue eget, auctor vitae massa.
        </div>
    </div>
</body>
</html>
"""

# Save the HTML content to a file
with open("bus_arrival_times.html", "w") as f:
    f.write(html_content)

print("HTML file with embedded Plotly plot and statistics has been generated.")
