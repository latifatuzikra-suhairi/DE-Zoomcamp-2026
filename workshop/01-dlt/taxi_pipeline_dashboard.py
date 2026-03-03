import marimo

__generated_with = "0.20.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import ibis
    from ibis import _
    import altair as alt

    return alt, ibis, mo


@app.cell
def _(mo):
    mo.md(r"""
    # 🚖 NYC Taxi Pipeline Dashboard
    """)
    return


@app.cell
def _(ibis):
    # 1. Database Connection
    con = ibis.connect("taxi_pipeline.duckdb")
    # Pastikan nama database/schema sesuai dengan dataset dlt Anda
    t = con.table("nyc_taxi_trips", database="taxi_pipeline_dataset")
    return (t,)


@app.cell
def _(t):
    # 2. Data Preparation with Integrity Fix

    # Pickup Trends
    p_mutated = t.mutate(date=t.trip_pickup_date_time.cast("timestamp").date())
    pickup_df = (
        p_mutated.group_by("date")
        .aggregate(count=p_mutated.count())
        .execute()
        .sort_values("date")
    )

    # Dropoff Trends
    d_mutated = t.mutate(date=t.trip_dropoff_date_time.cast("timestamp").date())
    dropoff_df = (
        d_mutated.group_by("date")
        .aggregate(count=d_mutated.count())
        .execute()
        .sort_values("date")
    )

    # Payment Stats (Pie)
    payment_stats = (
        t.group_by("payment_type")
        .aggregate(trip_count=t.count())
        .execute()
        .dropna(subset=['payment_type'])
    )

    # Tips Stats (Bar)
    tips_stats = (
        t.group_by("payment_type")
        .aggregate(total_tips=t.tip_amt.cast("float64").sum())
        .execute()
        .dropna()
    )
    return dropoff_df, payment_stats, pickup_df, tips_stats


@app.cell
def _(alt, dropoff_df, pickup_df):
    # 3. Line Chart Visualizations with Start & End Ticks

    # Define start and end dates for ticks
    p_ticks = [pickup_df['date'].min(), pickup_df['date'].max()]
    d_ticks = [dropoff_df['date'].min(), dropoff_df['date'].max()]

    p_chart = (
        alt.Chart(pickup_df)
        .mark_line(point=True, color="#4c78a8")
        .encode(
            x=alt.X("date:T", title="Date", axis=alt.Axis(values=p_ticks, format="%b %d")),
            y=alt.Y("count:Q", title="Trips"),
            tooltip=[
                alt.Tooltip("date:T", title="Pickup Date"), 
                alt.Tooltip("count:Q", title="Total Trips")
            ]
        )
        .properties(title="Daily Pickup Volume", width=400)
    )

    d_chart = (
        alt.Chart(dropoff_df)
        .mark_line(point=True, color="#f58518")
        .encode(
            x=alt.X("date:T", title="Date", axis=alt.Axis(values=d_ticks, format="%b %d")),
            y=alt.Y("count:Q", title="Trips"),
            tooltip=[
                alt.Tooltip("date:T", title="Dropoff Date"), 
                alt.Tooltip("count:Q", title="Total Trips")
            ]
        )
        .properties(title="Daily Dropoff Volume", width=400)
    )
    return d_chart, p_chart


@app.cell
def _(alt, payment_stats, tips_stats):
    # 4. Payment and Tips Visualizations

    # Pie Chart with Percentage
    pie = (
        alt.Chart(payment_stats)
        .transform_joinaggregate(total='sum(trip_count)')
        .transform_calculate(pct='datum.trip_count / datum.total')
        .mark_arc()
        .encode(
            theta=alt.Theta("trip_count:Q"),
            color=alt.Color("payment_type:N", title="Payment Type"),
            tooltip=[
                alt.Tooltip("payment_type:N"),
                alt.Tooltip("trip_count:Q", title="Count", format=","),
                alt.Tooltip("pct:Q", title="Percentage", format=".1%")
            ]
        )
        .properties(title="Proportion of Payment Types", width=350)
    )

    # Bar Chart for Tips
    bar = (
        alt.Chart(tips_stats)
        .mark_bar()
        .encode(
            x=alt.X("payment_type:N", title="Payment Type"),
            y=alt.Y("total_tips:Q", title="Total Tips ($)"),
            color="payment_type:N",
            tooltip=[
                alt.Tooltip("payment_type:N"),
                alt.Tooltip("total_tips:Q", title="Total Tips", format="$.2f")
            ]
        )
        .properties(title="Total Tips per Payment Type", width=400)
    )
    return bar, pie


@app.cell
def _(d_chart, p_chart):
    p_chart, d_chart
    return


@app.cell
def _(pie):
    pie
    return


@app.cell
def _(bar):
    bar
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
