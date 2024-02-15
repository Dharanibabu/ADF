"""
    Module contains functions and classes which handles data.
"""

from pyspark.sql import SparkSession
import pandas as pd


class Model:
    """
        Data Model Class

        The object of this class is the primary source of data for this library. User can add attributes as per
        their use case needs. By default following attributes are available

        Attributes:
             datetime: dict contains the datatime object.
    """

    def __init__(self):
        """
            Usual Initializer
        """
        self.datetime = {}

    def __getattr__(self, item):
        """
            Method to safely return the value of the required attribute.
        :param item: name of the attribute to be returned from model
        :return: any if item is available else None
        """
        return self.__dict__.get(item, None)

    
class Payload:
    """
        Payload Model Class

        This class is the model of the payload that is passed between the linked nodes. It holds the control flags to
        stop the runner process and the linked nodes.

        Attributes:
            data_model: `Model` object
    """

    def __init__(self):
        self._stop_runner = True
        self._stop_node = False
        self.data_model: Model = Model()


class Source:
    """
        Class contains connector to multiple datasources using which user can connect to datasource and fetch data
    """
    @staticmethod
    def read_csv(csv_path):
        return pd.read_csv(csv_path)

    class SparkHDFS:
        """
            Spark based HDFS connector.

            Class serves as HDFS datasource which is connected by spark.

            Attributes:
                spark: contains instance of spark session.
                fs: contains the instance of HDFS file system.
        """

        def __init__(self, base_url):
            """
                Usual Initializer
            :param base_url: HDFS url using which connection has to be established.
            """
            self._base_url = base_url
            self.spark = SparkSession.builder.appName('SparkHDFS').getOrCreate()
            self._sc = self.spark.sparkContext
            self._path = self._sc._gateway.jvm.org.apache.hadoop.fs.Path
            self.fs = (self._sc._jvm.org.apache.hadoop.fs.FileSystem.get(
                self._sc._gateway.jvm.java.net.URI(self._base_url),
                self._sc._jsc.hadoopConfiguration()
            ))
        
        def read_json(self, file_path):
            """
                Method to read json from HDFS
            :param file_path: path of the file to be read.
            :return: json
            """
            file_path = self._base_url+file_path
            return self.spark.read.json(file_path)

