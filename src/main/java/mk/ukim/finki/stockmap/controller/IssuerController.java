package mk.ukim.finki.stockmap.controller;

import mk.ukim.finki.stockmap.model.CsvData;
import mk.ukim.finki.stockmap.service.IssuerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import java.io.*;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Controller
public class IssuerController {

    @Autowired
    private IssuerService csvDataService;

    private List<CsvData> allData;

    @GetMapping("/")
    public String index(Model model) {
        allData = csvDataService.readCsvData();


        List<String> issuers = allData.stream()
                .map(CsvData::getIssuer)
                .distinct()
                .sorted()
                .collect(Collectors.toList());

        model.addAttribute("issuers", issuers);
        return "issuerData";
    }


    @PostMapping("/filter")
    public String filterData(@RequestParam("issuer") String issuer, Model model) {
        List<CsvData> filteredData = allData.stream()
                .filter(data -> data.getIssuer().equals(issuer))
                .collect(Collectors.toList());

        List<String> dates = filteredData.stream()
                .map(CsvData::getDate)
                .collect(Collectors.toList());

        List<String> closingPrices = filteredData.stream()
                .map(CsvData::getClose)
                .collect(Collectors.toList());




        model.addAttribute("dates", dates);
        model.addAttribute("closingPrices", closingPrices);
        model.addAttribute("filteredData", filteredData);
        model.addAttribute("issuers", allData.stream()
                .map(CsvData::getIssuer)
                .distinct()
                .sorted()
                .collect(Collectors.toList()));
        return "issuerData";
    }


    private List<String> readIndicatorsFromCsv(String filePath) {
        List<String> indicators = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader("./technical_indicators.csv"))) {
            String line;
            while ((line = br.readLine()) != null) {
                indicators.add(line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return indicators;
    }


    @PostMapping("/analyze")
    public String analyzeData(@RequestParam("issuer") String issuer, Model model) {

        List<CsvData> filteredData = allData.stream()
                .filter(data -> data.getIssuer().equals(issuer))
                .collect(Collectors.toList());



        try {
            ProcessBuilder processBuilder = new ProcessBuilder(
                    "python", "./technical_analysis.py"
            );
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line); // Може да се обработат резултатите од Python
                }
            }
            process.waitFor();
        } catch (Exception e) {
            e.printStackTrace();
        }


        List<String> indicators = readIndicatorsFromCsv("./technical_indicators.csv");
        model.addAttribute("indicators", indicators);

        return "issuerData";
    }

    @GetMapping("/home")
    public String loadHomePage() {
        return "home";
    }


    @GetMapping("/aboutUs")
    public String loadAboutUsPage() {
        return "aboutUs";
    }

}



