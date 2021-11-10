"""
CSV parsing classes.
"""

import csv
from typing import List, Optional


__all__ = ['CsvParser']


class CsvParserIterator:
    """
    CsvParser iterator.
    """

    def __init__(self, input_stream, csv_reader, skip_header: bool, cycle_reading: bool):
        """
        Constructor.

        :param input_stream: input CSV stream, file-like object.
        :param csv_reader: Reader instance.
        :param skip_header: skip CSV header if True.
        :param cycle_reading: loop reading flag.
        """

        self._input_stream = input_stream
        self._csv_reader = csv_reader
        self._skip_header = skip_header
        self._cycle_reading = cycle_reading

    def __next__(self):
        try:
            return next(self._csv_reader)
        except StopIteration:
            if not self._cycle_reading:
                raise

            self._input_stream.seek(0)
            if self._skip_header:
                next(self._csv_reader)

        return next(self._csv_reader)


class CsvParser:
    """
    CsvParser can read data from the CSV file.
    """

    def __init__(self, csv_file, loop=False):
        """
        Constructor.

        :param csv_file: file stream object or filename.
        :param loop: loop reading.
        """

        if isinstance(csv_file, str):
            self._csv_stream = open(csv_file, 'r')
        else:
            self._csv_stream = csv_file

        self._loop = loop
        self._header_presented = False
        self._header = None
        self._csv_reader = self._create_loader_stream()

    @property
    def header_presented(self) -> bool:
        """
        File has header?
        """

        return self._header_presented

    @property
    def header(self) -> Optional[List[...]]:
        """
        File header data.
        """

        return self._header

    def head(self):
        """
        Return first row of the CSV.

        :return: data.
        """

        self._seek_to_start()
        return next(self._csv_reader)

    def tail(self):
        """
        Return last row of the CSV.

        :return: data.
        """

        self._seek_to_start()

        # TODO: Improve speed!
        row = None
        for row in self._csv_reader:
            pass

        return row

    def _seek_to_start(self):
        """
        Seek to the start of the CSV stream and skip the header, if presented.
        """

        self._csv_stream.seek(0)

        if self._header_presented:
            # Skip it.
            return next(self._csv_reader)

    def _create_loader_stream(self):
        """
        Create CSV reader stream with correct dialect and a header skipping flag.

        :return: header flag and reader.
        """

        csv_sniffer = csv.Sniffer()

        dialect = csv_sniffer.sniff(self._csv_stream.read(1024))
        self._csv_stream.seek(0)
        self._header_presented = csv_sniffer.has_header(self._csv_stream.read(1024))
        self._header = self._seek_to_start()

        return csv.reader(self._csv_stream, dialect=dialect)

    def __iter__(self):
        """
        Create CSV iterator.

        :return: iterator.
        """

        self._seek_to_start()

        return CsvParserIterator(self._csv_stream, self._csv_reader, self.header_presented, self._loop)
