from flask import Flask, render_template, request
import numpy as np
from scipy.stats import t

app = Flask(__name__)

def ttest(data, mu0, alpha=0.05, alternative="two-sided"):
    data = np.array(data)
    n = len(data)

    xbar = np.mean(data)
    s = np.std(data, ddof=1)

    se = s / np.sqrt(n)

    t_cal = (xbar - mu0) / se
    df = n - 1

    if alternative == "two-sided":
        t_crit = t.ppf(1 - alpha/2, df)
        p_value = 2 * (1 - t.cdf(abs(t_cal), df))
        reject = abs(t_cal) > t_crit

    elif alternative == "greater":
        t_crit = t.ppf(1 - alpha, df)
        p_value = 1 - t.cdf(t_cal, df)
        reject = t_cal > t_crit

    elif alternative == "less":
        t_crit = t.ppf(alpha, df)
        p_value = t.cdf(t_cal, df)
        reject = t_cal < t_crit

    return {
        "xbar": round(xbar, 4),
        "s": round(s, 4),
        "t_cal": round(t_cal, 4),
        "df": df,
        "p_value": round(p_value, 6),
        "decision": "Reject H0" if reject else "Fail to Reject H0"
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        data_input = request.form["data"]
        mu0 = float(request.form["mu0"])
        alpha = float(request.form["alpha"])
        alternative = request.form["alternative"]

        # Convert comma-separated string to list of floats
        data = list(map(float, data_input.split(",")))

        result = ttest(data, mu0, alpha, alternative)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
    <!DOCTYPE html>
<html>
<head>
    <title>T-Test Calculator</title>
</head>
<body>
    <h2>One Sample T-Test</h2>

    <form method="POST">
        <label>Enter Data (comma separated):</label><br>
        <input type="text" name="data" required><br><br>

        <label>Hypothesized Mean (μ0):</label><br>
        <input type="number" step="any" name="mu0" required><br><br>

        <label>Significance Level (α):</label><br>
        <input type="number" step="any" name="alpha" value="0.05" required><br><br>

        <label>Alternative Hypothesis:</label><br>
        <select name="alternative">
            <option value="two-sided">Two-Sided</option>
            <option value="greater">Greater</option>
            <option value="less">Less</option>
        </select><br><br>

        <button type="submit">Calculate</button>
    </form>

    {% if result %}
        <h3>Results:</h3>
        <p>Sample Mean: {{ result.xbar }}</p>
        <p>Sample Std Dev: {{ result.s }}</p>
        <p>T Statistic: {{ result.t_cal }}</p>
        <p>Degrees of Freedom: {{ result.df }}</p>
        <p>P-Value: {{ result.p_value }}</p>
        <p><strong>Decision: {{ result.decision }}</strong></p>
    {% endif %}

</body>
</html>