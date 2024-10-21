# Import other modules not related to PySpark
import os
import sys
import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import math
from IPython.core.interactiveshell import InteractiveShell
from datetime import *
import statistics as stats

matplotlib.rcParams["figure.dpi"] = 100
InteractiveShell.ast_node_interpurchase = "all"
# %matplotlib inline

# Import PySpark related modules
import pyspark
from pyspark.rdd import RDD
from pyspark.sql import Row
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql import functions
from pyspark.sql.functions import (
    lit,
    desc,
    col,
    size,
    array_contains,
    isnan,
    udf,
    hour,
    array_min,
    array_max,
    countDistinct,
)

import pyspark.sql.functions as f

from pyspark.sql.types import *

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
    spark_df.describe().toPandas()
    print(f"There are total {spark_df.count()} rows")
    print(spark_df.limit(5).toPandas())
    return spark_df


def save_sample_data(df, filepath, nrows=100):
    '''
    extract random sample data of nrows sample in <filename_path>
    '''
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
    if verbose>0:
        print(f" timestamp_columns [size= {len(timestamp_columns)}] = {timestamp_columns}")
        print(f" string_columns [size= {len(string_columns)}] = {string_columns}")
        print(f" numeric_columns [size= {len(numeric_columns)}] = {numeric_columns}")
        print(f" array_columns [size= {len(array_columns)}] = {array_columns}")
        print(f" unkown_columns [size= {len(unkown_columns)}] = {unkown_columns}")

    return string_columns, numeric_columns, array_columns, timestamp_columns, unkown_columns


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


def plot_columns(df, x_column, y_columns, subplot=True):
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
    if subplot:
        fig.suptitle("Explore the dataframe time series", fontsize=14)
    else:
        plt.title("Explore the dataframe time series")
    # show the canvas
    plt.show()


def generate_explode(nb_categories):
    explode = [1 / nb_categories for k in range(nb_categories)]
    return explode


def data_preparation_pipeline(spark, spark_df):
    # remove the invalid value (negative price, quantity, others)
    nb_invalid_values = spark_df.select("*")\
            .where((col("Price")<0) | \
                (col("Quantity")<0) | \
                (col("Purch_Amt")<0) | \
                (col("Returns")<0) | \
                (col("Churn")<0)  ).count()
    total_nb_samples = spark_df.count()

    if nb_invalid_values>=0:
        print(
            f"- {nb_invalid_values}/{total_nb_samples} invalid (negative) values found!!. \
                \n {100*nb_invalid_values/total_nb_samples}% samples were removed from the dataset "
        )
        spark_df = spark_df.select("*")\
                            .where((col("Price")>=0) & \
                                (col("Quantity")>=0) & \
                                (col("Purch_Amt")>=0) & \
                                (col("Returns")>=0) & \
                                (col("Churn")>=0)  )

    # remove the invalid computation(s) of Purch_Amt=Price*Quantity
    nb_invalid_Purch_Amt_values = spark_df.select("*")\
            .where((col("Price")*col("Quantity")!=col("Purch_Amt")) ).count()
    total_nb_samples = spark_df.count()

    if nb_invalid_Purch_Amt_values>=0:
        print(
            f"- {nb_invalid_Purch_Amt_values}/{total_nb_samples} invalid computation(s) of Purch_Amt=Price*Quantity are found!!. \
                \n {100*nb_invalid_Purch_Amt_values/total_nb_samples}% samples were removed from the dataset "
        )
        spark_df = spark_df.select("*")\
                            .where((col("Price")*col("Quantity")==col("Purch_Amt")) )

    # count the missing values
    missing_invalid_df = count_missing_invalid_values(spark_df)

    return spark_df, missing_invalid_df


def data_analysis_pipeline(spark, spark_df):

    # calculate sum of sales by month
    monthly_spark_df=spark_df.groupBy(f.year("Date").alias("year"), f.month("Date").alias("month"))\
                             .agg(f.sum("Purch_Amt").alias("sum_Purch_Amt"),
                                f.avg("Purch_Amt").alias("avg_Purch_Amt"),
                                f.avg("Price").alias("avg_Price"),
                                f.avg("Quantity").alias("avg_Quantity"),
                                f.sum("Quantity").alias("sum_Quantity"),
                                f.avg("Age").alias("avg_Age"),
                                f.sum("Returns").alias("sum_Returns"),
                                f.sum("Churn").alias("sum_Churn")
                                )
    monthly_spark_df=monthly_spark_df.select(*[f.round(c, 2).alias(c) for c in monthly_spark_df.columns])
    monthly_spark_df = monthly_spark_df.withColumn("DateByMonth", f.expr("make_date(year, month, 1)")).orderBy("DateByMonth")
    monthly_spark_df.show()

    return monthly_spark_df.toPandas()


def data_modeling_pipeline():

    return {}


def model_deployment_pipeline():

    return {}
