package mk.ukim.finki.stockmap.service;

import mk.ukim.finki.stockmap.model.CsvData;
import org.springframework.stereotype.Service;
import java.io.*;
import java.util.*;


import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.springframework.stereotype.Service;

import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@Service
public class IssuerService {

    public List<CsvData> readCsvData() {
        List<CsvData> csvDataList = new ArrayList<>();

        try (FileReader reader = new FileReader(Paths.get("C:\\Users\\mihai\\Videos\\StockMap\\src\\main\\java\\stock_data.csv").toFile())) {
            Iterable<CSVRecord> records = CSVFormat.DEFAULT.withFirstRecordAsHeader().parse(reader);

            for (CSVRecord record : records) {
                CsvData csvData = new CsvData();
                csvData.setIssuer(record.get("Issuer"));
                csvData.setDate(record.get("Date"));
                csvData.setOpen(record.get("Open"));
                csvData.setHigh(record.get("High"));
                csvData.setLow(record.get("Low"));
                csvData.setClose(record.get("Close"));
                csvData.setChange(record.get("Change"));
                csvData.setVolume(record.get("Volume"));
                csvData.setTurnover(record.get("Turnover"));
                csvData.setMarketCap(record.get("Market Cap"));

                csvDataList.add(csvData);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return csvDataList;
    }
}
