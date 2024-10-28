# Import other modules not related to PySpark
import json
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# Import PySpark related modules
import pyspark
import pyspark.sql.functions as f
from IPython.core.interactiveshell import InteractiveShell
from pyspark.sql import SparkSession
from pyspark.sql.functions import array_contains, col

# from pyspark.sql.types import *

# from datetime import *
matplotlib.rcParams["figure.dpi"] = 100
InteractiveShell.ast_node_interpurchase = "all"


# %matplotlib inline
def init_spark(MAX_MEMORY="15G"):
    # Initialize a spark session.
    conf = (
        pyspark.SparkConf()
        .setMaster("local[*]")
        .set("spark.executor.heartbeatInterval", 10000)
        .set("spark.network.timeout", 10000)
        .set("spark.core.connection.ack.wait.timeout", "3600")
        .set("spark.executor.memory", MAX_MEMORY)
        .set("spark.driver.memory", MAX_MEMORY)
    )
    # initait ethe sperk session
    spark = (
        SparkSession.builder.appName("Pyspark guide").config(conf=conf).getOrCreate()
    )
    return spark


def spark_load_data(spark, filename_path):
    df = pd.read_excel(filename_path)
    spark_df = spark.createDataFrame(df)
    spark_df = spark_df.orderBy("Date")

    # displays
    # spark_df.toPandas().describe()
    print(f"There are total {spark_df.count()} rows")
    print("Raw data :", spark_df.limit(5).toPandas())
    return spark_df


def save_sample_data(df, filepath, nrows=100):
    """
    extract random sample data of nrows sample in <filename_path>
    """
    filename, file_extension = os.path.splitext(filepath)
    # extract random sample data of nrows samples
    df_sample = df.sample(n=nrows).reset_index().drop(columns="index")
    print(df_sample.head())

    # save file-like object for CSV reader
    if file_extension == ".xlsx":
        df_sample.to_excel(filepath, index=False)
    elif file_extension == ".csv":
        df_sample.to_csv(filepath)
    else:
        raise Exception(
            f"Invalid file extension ({file_extension}). Please upload CSV/xlsx file types."
        )


def categorize_columns(spark_df, verbose=1):
    string_columns = []
    numeric_columns = []
    array_columns = []
    timestamp_columns = []
    unkown_columns = []
    for col_name, data_type in spark_df.dtypes:
        # print(f"({col_name},{col_name})")
        if data_type == "string":
            string_columns.append(col_name)
        elif data_type == "array":
            array_columns.append(col_name)
        elif data_type == "timestamp":
            timestamp_columns.append(col_name)
        elif (
            "int" in data_type
            or "long" in data_type
            or "float" in data_type
            or "double" in data_type
        ):
            numeric_columns.append(col_name)
        else:
            unkown_columns.append((col_name, data_type))
    if verbose > 0:
        print(
            f" timestamp_columns [size= {len(timestamp_columns)}] = {timestamp_columns}"
        )
        print(f" string_columns [size= {len(string_columns)}] = {string_columns}")
        print(f" numeric_columns [size= {len(numeric_columns)}] = {numeric_columns}")
        print(f" array_columns [size= {len(array_columns)}] = {array_columns}")
        print(f" unkown_columns [size= {len(unkown_columns)}] = {unkown_columns}")

    return (
        string_columns,
        numeric_columns,
        array_columns,
        timestamp_columns,
        unkown_columns,
    )


def count_missing_invalid_values(spark_df):
    # get the columns categories
    (
        string_columns,
        numeric_columns,
        array_columns,
        timestamp_columns,
        unkown_columns,
    ) = categorize_columns(spark_df, verbose=0)
    #  count the missing values
    missing_values = {}
    for index, column in enumerate(spark_df.columns):
        if column in string_columns:  # check string columns with None and Null values
            missing_count = spark_df.filter(
                col(column).eqNullSafe(None) | col(column).isNull()
            ).count()
            missing_values.update({column: missing_count})

        if column in numeric_columns:  # check None, NaN
            missing_count = spark_df.where(col(column).isin([None, np.nan])).count()
            missing_values.update({column: missing_count})

        if column in timestamp_columns:  # check Null
            missing_count = spark_df.filter(
                col(column).eqNullSafe(None) | col(column).isNull()
            ).count()
            missing_values.update({column: missing_count})

        if column in array_columns:  # check zeros and NaN
            missing_count = spark_df.filter(
                array_contains(spark_df[column], 0)
                | array_contains(spark_df[column], np.nan)
            ).count()
            missing_values.update({column: missing_count})
    # count the missing percentage
    nb_samples = 100 / spark_df.count()  # normalization factor
    missing_values_percentage = {
        column: nb_samples * missing_count
        for (column, missing_count) in missing_values.items()
    }

    # show the mising values table
    missing_invalid_df = pd.DataFrame(missing_values, index=["count"])
    missing_percentage_df = pd.DataFrame(
        missing_values_percentage, index=["percentage"]
    )
    missing_invalid_df = pd.concat([missing_invalid_df, missing_percentage_df])
    return missing_invalid_df


def plot_columns(df, x_column, y_columns, title="", subplot=True):
    import matplotlib.pyplot as plt

    x_ts = [val[x_column] for val in df.select(x_column).collect()]
    if subplot:
        fig, axs = plt.subplots(len(y_columns))
    for idx, y_column in enumerate(y_columns):
        y_ans_val = [val[y_column] for val in df.select(y_column).collect()]
        if subplot:
            axs[idx].plot(x_ts, y_ans_val, label=y_column)
            axs[idx].legend()  # loc="upper left")
            if idx < len(y_columns) - 1:
                axs[idx].set_xticks([])
        else:
            plt.plot(x_ts, y_ans_val, label=y_column)

    plt.xticks(rotation=80)
    plt.xlabel(x_column)
    plt.legend()  # loc="upper left")
    #  set the title
    if title == "":
        title = "Explore time-series variation"

    if subplot:
        fig.suptitle(title, fontsize=14)
    else:
        plt.title(title)
    # show the canvas
    plt.show()


def save_dict_to_json(dict_, filepath):
    # Save dict to JSON file
    with open(filepath, "w") as outfile:
        json.dump(dict_, outfile)
    outfile.close()


def load_dict_from_json(filepath):
    # read json file
    with open(filepath, "r") as file:
        dict_ = json.load(file)
    file.close()
    return dict_


def generate_explode(nb_categories):
    explode = [1 / nb_categories for k in range(nb_categories)]
    return explode


def data_preparation_pipeline(spark, spark_df):
    print(f"\n\n - data preparation in process ...")

    # Replace 0 for null on only population column
    spark_df = spark_df.na.fill(value=0, subset=["Returns"])

    # remove the invalid value (negative price, quantity, others)
    nb_invalid_values = (
        spark_df.select("*")
        .where(
            (col("Price") < 0)
            | (col("Quantity") < 0)
            | (col("Purch_Amt") < 0)
            | (col("Returns") < 0)
            | (col("Churn") < 0)
        )
        .count()
    )
    total_nb_samples = spark_df.count()

    if nb_invalid_values >= 0:
        print(
            f"- {nb_invalid_values}/{total_nb_samples} invalid (negative) values found!!. \
                \n {100*nb_invalid_values/total_nb_samples}% samples were removed from the dataset "
        )
        spark_df = spark_df.select("*").where(
            (col("Price") >= 0)
            & (col("Quantity") >= 0)
            & (col("Purch_Amt") >= 0)
            & (col("Returns") >= 0)
            & (col("Churn") >= 0)
        )

    # remove the invalid computation(s) of Purch_Amt=Price*Quantity
    nb_invalid_Purch_Amt_values = (
        spark_df.select("*")
        .where((col("Price") * col("Quantity") != col("Purch_Amt")))
        .count()
    )
    total_nb_samples = spark_df.count()

    if nb_invalid_Purch_Amt_values >= 0:
        print(
            f"- {nb_invalid_Purch_Amt_values}/{total_nb_samples} invalid computation(s) of Purch_Amt=Price*Quantity are found!!. \
                \n {100*nb_invalid_Purch_Amt_values/total_nb_samples}% samples were removed from the dataset "
        )
        spark_df = spark_df.select("*").where(
            (col("Price") * col("Quantity") == col("Purch_Amt"))
        )

    # count the missing values
    missing_invalid_df = count_missing_invalid_values(spark_df)

    return spark_df, missing_invalid_df


# -- rank ales by product category
def rank_sales_by_product_category(spark_df, topN=5):
    ranked_product_category_spark_df = (
        spark_df.select(spark_df.Category, spark_df.Cust_ID, spark_df.Date)
        .groupBy(spark_df.Category)
        .count()
        .orderBy("count", ascending=False)
    )

    # Top 5 purchase types
    ranked_product_category_df = ranked_product_category_spark_df.limit(topN).toPandas()
    # Rename column name : "count" --> Clients count
    ranked_product_category_df.rename(columns={"count": "Clients count"}, inplace=True)

    # Calculate the total users, we will this result to compute percentage later
    total_categories_clients = (
        ranked_product_category_spark_df.groupBy().sum().collect()[0][0]
    )

    # Compute the percentage of top 5 purchase type / total users
    ranked_product_category_df["percentage"] = (
        ranked_product_category_df["Clients count"] / total_categories_clients * 100
    )

    return total_categories_clients, ranked_product_category_df


# -- calculate sum of sales by month
def daily_income_stats(spark_df):
    transactions_spark_df = spark_df.groupBy(
        f.year("Date").alias("year"),
        f.month("Date").alias("month"),
        f.day("Date").alias("day"),
    ).agg(
        f.sum("Cust_ID").alias("sum_Cust_ID"),
        f.sum("Purch_Amt").alias("sum_Purch_Amt"),
        f.avg("Purch_Amt").alias("avg_Purch_Amt"),
        f.avg("Price").alias("avg_Price"),
        f.avg("Quantity").alias("avg_Quantity"),
        f.sum("Quantity").alias("sum_Quantity"),
        f.avg("Age").alias("avg_Age"),
        f.sum("Returns").alias("sum_Returns"),
        f.sum("Churn").alias("sum_Churn"),
    )
    transactions_spark_df = transactions_spark_df.select(
        *[f.round(c, 2).alias(c) for c in transactions_spark_df.columns]
    )
    transactions_spark_df = transactions_spark_df.withColumn(
        "DateByPeriod", f.expr("make_date(year, month, day)")
    ).orderBy("DateByPeriod")

    return transactions_spark_df


def monthly_income_stats(spark_df):
    transactions_spark_df = spark_df.groupBy(
        f.year("Date").alias("year"), f.month("Date").alias("month")
    ).agg(
        f.sum("Cust_ID").alias("sum_Cust_ID"),
        f.sum("Purch_Amt").alias("sum_Purch_Amt"),
        f.avg("Purch_Amt").alias("avg_Purch_Amt"),
        f.avg("Price").alias("avg_Price"),
        f.avg("Quantity").alias("avg_Quantity"),
        f.sum("Quantity").alias("sum_Quantity"),
        f.avg("Age").alias("avg_Age"),
        f.sum("Returns").alias("sum_Returns"),
        f.sum("Churn").alias("sum_Churn"),
    )
    transactions_spark_df = transactions_spark_df.select(
        *[f.round(c, 2).alias(c) for c in transactions_spark_df.columns]
    )
    transactions_spark_df = transactions_spark_df.withColumn(
        "DateByPeriod", f.expr("make_date(year, month, 1)")
    ).orderBy("DateByPeriod")

    return transactions_spark_df


def yearly_income_stats(spark_df):
    transactions_spark_df = spark_df.groupBy(f.year("Date").alias("year")).agg(
        f.sum("Cust_ID").alias("sum_Cust_ID"),
        f.sum("Purch_Amt").alias("sum_Purch_Amt"),
        f.avg("Purch_Amt").alias("avg_Purch_Amt"),
        f.avg("Price").alias("avg_Price"),
        f.avg("Quantity").alias("avg_Quantity"),
        f.sum("Quantity").alias("sum_Quantity"),
        f.avg("Age").alias("avg_Age"),
        f.sum("Returns").alias("sum_Returns"),
        f.sum("Churn").alias("sum_Churn"),
    )
    transactions_spark_df = transactions_spark_df.select(
        *[f.round(c, 2).alias(c) for c in transactions_spark_df.columns]
    )
    transactions_spark_df = transactions_spark_df.withColumn(
        "DateByPeriod", f.expr("make_date(year, 1, 1)")
    ).orderBy("DateByPeriod")

    return transactions_spark_df


def get_transactions_per_period(spark_df, period="monthly"):

    if period == "daily":
        transactions_spark_df = daily_income_stats(spark_df)

    elif period == "monthly":
        transactions_spark_df = monthly_income_stats(spark_df)

    elif period == "yearly":
        transactions_spark_df = yearly_income_stats(spark_df)
    else:
        e = f"Error: period ={period} is not defined "
        raise Exception(e)

    # extract the needed metrics
    y_values = (
        transactions_spark_df.select("sum_Purch_Amt").rdd.flatMap(lambda x: x).collect()
    )
    date_values = (
        transactions_spark_df.select("DateByPeriod").rdd.flatMap(lambda x: x).collect()
    )
    date_values = [t.strftime("%Y-%b-%d") for t in date_values]
    stat_dic = {
        "date": date_values,
        "income": y_values,
    }
    return transactions_spark_df, stat_dic


# -- calculate sales growth
def get_current_part_sales(yearly_stats_spark_df, monthly_stats_spark_df):
    latest_operation = yearly_stats_spark_df.collect()[-1]
    latest_operation.year

    columns_list = [
        "year",
        "month",
        "sum_Cust_ID",
        "sum_Purch_Amt",
        "avg_Purch_Amt",
        "avg_Price",
        "sum_Quantity",
        "avg_Age",
        "sum_Returns",
        "sum_Churn",
        "DateByPeriod",
    ]

    current_sales = monthly_stats_spark_df.select(*columns_list).where(
        (f.col("year") >= latest_operation.year) & (f.col("year") >= 0)
    )

    start_current_period_operation = current_sales.collect()[0]
    end_current_period_operation = current_sales.collect()[-1]

    past_sales = monthly_stats_spark_df.select(*columns_list).where(
        (f.col("year") == start_current_period_operation.year - 1)
        & (f.col("month") >= start_current_period_operation.month)
        & (f.col("month") <= end_current_period_operation.month)
    )

    return past_sales, current_sales


def get_sales_windows_stats(sales_spark_df):
    growth_stats_spark_df = sales_spark_df.groupBy(f.col("year")).agg(
        f.sum("sum_Cust_ID").alias("sum_sum_Cust_ID"),
        f.sum("sum_Purch_Amt").alias("sum_sum_Purch_Amt"),
        f.avg("avg_Price").alias("avg_avg_Price"),
        f.sum("sum_Quantity").alias("sum_sum_Quantity"),
        f.avg("avg_Age").alias("avg_avg_Age"),
        f.sum("sum_Returns").alias("sum_sum_Returns"),
        f.sum("sum_Churn").alias("sum_sum_Churn"),
    )
    return growth_stats_spark_df.toPandas()


def compute_sales_growth(current_sales, past_sales):
    def compute_growth_metric(current_sales_stats_df, past_sales_stats_df, metric):
        return round(
            100
            * (current_sales_stats_df[metric][0] - past_sales_stats_df[metric][0])
            / past_sales_stats_df[metric][0],
            2,
        )

    #  compute the current and last growths
    current_sales_stats_df = get_sales_windows_stats(current_sales)
    past_sales_stats_df = get_sales_windows_stats(past_sales)

    #  sumamries the growth
    growth_rate_dict = {}
    for metric in current_sales_stats_df.columns:
        if metric == "year":
            growth_rate = current_sales_stats_df[metric][0]
        else:
            growth_rate = compute_growth_metric(
                current_sales_stats_df, past_sales_stats_df, metric=metric
            )
        growth_rate_dict.update(
            {metric.lstrip("sum_sum").lstrip("avg_avg_"): str(growth_rate)}
        )

    return past_sales_stats_df, current_sales_stats_df, growth_rate_dict


# rank sales by clients
def rank_sales_by_clients(spark_df, topN=5):

    transactions_spark_df = (
        spark_df.groupBy(spark_df.Cust_ID, spark_df.Name, spark_df.Age)
        .agg(
            f.count("Cust_ID").alias("transactions count"),
            f.min("Date").alias("first transactions"),
            f.max("Date").alias("latest transactions"),
            f.sum("Purch_Amt").alias("sum_Purch_Amt"),
            f.avg("Age").alias("avg_Age"),
            f.sum("Returns").alias("sum_Returns"),
            f.sum("Churn").alias("sum_Churn"),
        )
        .orderBy("transactions count", ascending=False)
        .toPandas()
    )

    transactions_spark_df["percentage"] = round(
        100
        * transactions_spark_df["sum_Purch_Amt"]
        / np.sum(transactions_spark_df["sum_Purch_Amt"]),
        2,
    )
    top_ranked_clients_df = transactions_spark_df[:topN]
    worst_ranked_clients_df = transactions_spark_df[-topN:]
    return top_ranked_clients_df, worst_ranked_clients_df


# rank sales by gender
def rank_sales_by_gender(spark_df, topN=5):
    purchases_by_gender = (
        spark_df.groupBy("Category", "Gender")
        .count()
        .orderBy("count", ascending=False)
        .toPandas()
    )
    top_purchases_by_gender_df = (
        purchases_by_gender.pivot_table(
            index="Category", columns="Gender", values="count", fill_value=0
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    top_purchases_by_gender_df["total"] = (
        top_purchases_by_gender_df["Male"] + top_purchases_by_gender_df["Female"]
    )
    top_purchases_by_gender_df["percentage"] = round(
        100
        * top_purchases_by_gender_df["total"]
        / np.sum(top_purchases_by_gender_df["total"]),
        2,
    )

    top_purchases_by_gender_df["MalePercentage"] = round(
        100 * top_purchases_by_gender_df["Male"] / top_purchases_by_gender_df["total"],
        2,
    )
    top_purchases_by_gender_df["FemalePercentage"] = round(
        100
        * top_purchases_by_gender_df["Female"]
        / top_purchases_by_gender_df["total"],
        2,
    )
    return purchases_by_gender, top_purchases_by_gender_df[:topN]


# plot sales by gender
def plot_sales_by_gender(spark_df):
    total_purchases = spark_df.count()
    purchases_by_gender = (
        spark_df.groupBy("Category", "Gender")
        .count()
        .orderBy("count", ascending=False)
        .toPandas()
    )
    print(
        f"There are total: {total_purchases} purchases and here is the chart for purchases based on gender:"
    )

    # Visualize
    nb_categories = len(np.unique(purchases_by_gender["Category"]))
    fig = plt.figure(figsize=(25, nb_categories))

    #  TODO : check the plot here
    # grid_size = (1, 1)
    # ax = plt.subplot2grid(grid_size, (0, 0), colspan=1, rowspan=1)
    # plot = (
    #     purchases_by_gender.groupby(["Category", "Gender"])
    #     .agg(np.mean)
    #     .groupby(level=0)
    #     .apply(lambda x: 100 * x / x.sum())
    #     .unstack()
    #     .plot(
    #         kind="barh",
    #         stacked=True,
    #         width=1,  # -- APPLY UNSTACK TO RESHAPE DATA
    #         edgecolor="black",
    #         ax=ax,
    #         title="List of all purchases by gender",
    #     )
    # )
    # ylabel = plt.ylabel("Category (Purchase)")
    # xlabel = plt.xlabel("Participation percentage by gender")
    # legend = plt.legend(
    #     sorted(purchases_by_gender["Gender"].unique()),
    #     loc="center left",
    #     bbox_to_anchor=(1.0, 0.5),
    # )
    # param_update = plt.rcParams.update({"font.size": 16})
    # ax = plt.gca()
    # formatter = ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    fig.tight_layout()
    plt.show()


def data_analysis_pipeline(spark, spark_df, topN=5, verbose=0):
    print(f"\n\n - data analysis in process ...")

    # compute the sales stats by periods: daily, monthly, yearly
    daily_stats_spark_df, daily_stat_dic = get_transactions_per_period(
        spark_df, period="daily"
    )
    monthly_stats_spark_df, monthly_stat_dic = get_transactions_per_period(
        spark_df, period="monthly"
    )
    yearly_stats_spark_df, yearly_stat_dic = get_transactions_per_period(
        spark_df, period="yearly"
    )

    # -- calculate sales growth
    past_sales, current_sales = get_current_part_sales(
        yearly_stats_spark_df, monthly_stats_spark_df
    )
    past_sales_stats_df, current_sales_stats_df, growth_rate_dict = (
        compute_sales_growth(current_sales, past_sales)
    )

    # rank sales by clients
    top_ranked_clients_df, worst_ranked_clients_df = rank_sales_by_clients(
        spark_df, topN=topN
    )

    if verbose > 0:
        print(f"\n - Total transactions {spark_df.count()}  \n\n\n Top{topN} clients :")
        print(top_ranked_clients_df)
        print(
            f"\n - Total transactions {spark_df.count()}  \n\n\n Worst{topN} clients :"
        )
        print(worst_ranked_clients_df)

    # rank sales by gender
    purchases_by_gender, top_purchases_by_gender_df = rank_sales_by_gender(
        spark_df, topN=topN
    )
    # compute ratios
    ratio_female = round(100*np.sum(top_purchases_by_gender_df["Female"])\
                            /(np.sum(top_purchases_by_gender_df["Male"] + top_purchases_by_gender_df["Female"]))
                        ,2)
    ratio_male = 100-ratio_female
    ratio_gender_dict={"Male": str(round(ratio_male,1)), "Female": str(round(ratio_female,1))}

    return (
        growth_rate_dict,
        ratio_gender_dict,
        monthly_stats_spark_df.toPandas(),
        yearly_stats_spark_df.toPandas(),
        past_sales_stats_df,
        current_sales_stats_df,
        top_ranked_clients_df,
        worst_ranked_clients_df,
        top_purchases_by_gender_df,
    )


def data_modeling_pipeline():
    print(f"\n\n - data modeling in process ...")

    return {}


def model_deployment_pipeline():
    print(f"\n\n - model deployment in process ...")

    return {}


def get_widget_info(value, rate):
    """
    build the attributes of the dashboard widget
    """
    if rate > 0:
        arrow = "cilArrowTop"
        color = "color:green;"
    elif rate == 0:
        arrow = ""
        color = "color:gray;"
    else:
        arrow = "cilArrowBottom"
        color = "color:red;"

    widget_dic = {
        "value": "{:,}$".format(value),
        "rate": rate,
        "arrow": arrow,
        "color": color,
    }

    return widget_dic


def full_preparation_modeling_pipelines(filename_path):
    # ---------------------------------------------------------------
    # initialize the spark sessions
    spark = init_spark(MAX_MEMORY="4G")

    # Load the main data set into pyspark data frame
    spark_df = spark_load_data(spark, filename_path)

    # ---------------------------------------------------------------
    # run the  data preparation pipeline
    spark_df, missing_invalid_df = data_preparation_pipeline(spark, spark_df)

    # run the data analysis pipeline
    (
        growth_rate_dict,
        ratio_gender_dict,
        monthly_stats_df,
        yearly_stats_df,
        past_sales_stats_df,
        current_sales_stats_df,
        top_ranked_clients_df,
        worst_ranked_clients_df,
        top_purchases_by_gender_df,
    ) = data_analysis_pipeline(spark, spark_df, topN=5, verbose=0)

    # prepare the API dict
    data_dict, stats_dict = prepare_the_API_dicts(
        growth_rate_dict,
        ratio_gender_dict,
        monthly_stats_df,
        yearly_stats_df,
        past_sales_stats_df,
        current_sales_stats_df,
        top_ranked_clients_df,
        worst_ranked_clients_df,
        top_purchases_by_gender_df,
    )

    return data_dict, stats_dict


def prepare_the_API_dicts(
    growth_rate_dict,
    ratio_gender_dict,
    monthly_stats_df,
    yearly_stats_df,
    past_sales_stats_df,
    current_sales_stats_df,
    top_ranked_clients_df,
    worst_ranked_clients_df,
    top_purchases_by_gender_df,
):

    # ---------------------------------------------------------------
    # data_dict = df.astype(str).to_dict(orient="records")  # orient="list")

    # Tables dict
    data_dict = {}
    # monthly sales
    data_dict.update(
        {"monthly_sales": monthly_stats_df.round(1).astype(str).to_dict(orient="records")}
    )
    # yearly sales
    data_dict.update(
        {"yearly_sales": yearly_stats_df.round(1).astype(str).to_dict(orient="records")}
    )

    # Past sales
    data_dict.update(
        {
            "past_sales": past_sales_stats_df.round(1)
            .astype(str)
            .to_dict(orient="records")
        }
    )
    # Current sales
    data_dict.update(
        {
            "current_sales": current_sales_stats_df.round(1)
            .astype(str)
            .to_dict(orient="records")
        }
    )
    # Top Clients
    data_dict.update(
        {
            "top_ranked_clients": top_ranked_clients_df.round(1)
            .astype(str)
            .to_dict(orient="records")
        }
    )


    # stats dictionary
    stats_dict = {}
    stats_dict.update({"growth_rate": growth_rate_dict})

    # -- Customer
    customer_dic = get_widget_info(value=19960, rate=-3.9)
    stats_dict.update({"Customer": customer_dic})

    # -- Income
    growth_dic = get_widget_info(value=15250, rate=-5.5)
    stats_dict.update({"Income": growth_dic})

    # -- Customer
    price_dic = get_widget_info(value=190, rate=0.5)
    stats_dict.update({"Price": price_dic})

    # -- Returns
    returns_dic = get_widget_info(value=65, rate=-0.5)
    stats_dict.update({"Returns": returns_dic})

    # -- Churns
    churns_dic = get_widget_info(value=10, rate=1.5)
    stats_dict.update({"Churns": churns_dic})

    # display

    print(f"stats_dict={stats_dict}")
    print(f"data_dict={data_dict}")

    return data_dict, stats_dict


def demo_preparation_modeling_pipelines():
    growth_rate_dict = load_dict_from_json(filepath="data/test/growth_rate_dict.json")
    ratio_gender_dict = load_dict_from_json(filepath="data/test/ratio_gender_dict.json")

    yearly_stats_df = pd.DataFrame(
        load_dict_from_json(filepath="data/test/yearly_stats_spark_df.json")
    )
    monthly_stats_df = pd.DataFrame(
        load_dict_from_json(filepath="data/test/monthly_stats_spark_df.json")
    )
    past_sales_stats_df = pd.DataFrame(
        load_dict_from_json(filepath="data/test/past_sales_stats_df.json")
    )
    current_sales_stats_df = pd.DataFrame(
        load_dict_from_json(filepath="data/test/current_sales_stats_df.json")
    )
    top_ranked_clients_df = pd.DataFrame(
        load_dict_from_json(filepath="data/test/top_ranked_clients_df.json")
    )
    worst_ranked_clients_df = pd.DataFrame(
        load_dict_from_json(filepath="data/test/worst_ranked_clients_df.json")
    )
    top_purchases_by_gender_df = pd.DataFrame(
        load_dict_from_json(filepath="data/test/top_purchases_by_gender_df.json")
    )

    # prepare the API dict
    data_dict, stats_dict =prepare_the_API_dicts(
        growth_rate_dict,
        ratio_gender_dict,
        monthly_stats_df,
        yearly_stats_df,
        past_sales_stats_df,
        current_sales_stats_df,
        top_ranked_clients_df,
        worst_ranked_clients_df,
        top_purchases_by_gender_df,
    )

    return data_dict, stats_dict


# def save_resutls_to_json():
#     # save the results in json files
#     save_dict_to_json(ratio_gender_dict, filepath="data/test/ratio_gender_dict.json")
#     save_dict_to_json(growth_rate_dict, filepath="data/test/growth_rate_dict.json")

#     save_dict_to_json(current_sales.toPandas().astype(str).to_dict(orient="records"), filepath="data/test/current_sales.json")
#     save_dict_to_json(past_sales.toPandas().astype(str).to_dict(orient="records"), filepath="data/test/past_sales.json")
#     save_dict_to_json(past_sales_stats_df.astype(str).to_dict(orient="records"), filepath="data/test/past_sales_stats_df.json")
#     save_dict_to_json(current_sales_stats_df.astype(str).to_dict(orient="records"), filepath="data/test/current_sales_stats_df.json")
#     save_dict_to_json(past_sales.toPandas().astype(str).to_dict(orient="records"), filepath="data/test/past_sales.json")

#     save_dict_to_json(top_ranked_clients_df.astype(str).to_dict(orient="records"), filepath="data/test/top_ranked_clients_df.json")
#     save_dict_to_json(worst_ranked_clients_df.astype(str).to_dict(orient="records"), filepath="data/test/worst_ranked_clients_df.json")

#     save_dict_to_json(top_purchases_by_gender_df.astype(str).to_dict(orient="records"), filepath="data/test/top_purchases_by_gender_df.json")
#     save_dict_to_json(ranked_product_category_df.astype(str).to_dict(orient="records"), filepath="data/test/ranked_product_category_df.json")
#     save_dict_to_json(monthly_stats_spark_df.toPandas().astype(str).to_dict(orient="records"), filepath="data/test/monthly_stats_spark_df.json")
#     save_dict_to_json(yearly_stats_spark_df.toPandas().astype(str).to_dict(orient="records"), filepath="data/test/yearly_stats_spark_df.json")
