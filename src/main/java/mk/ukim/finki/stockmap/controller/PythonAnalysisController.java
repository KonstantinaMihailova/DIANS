package mk.ukim.finki.stockmap.controller;


import mk.ukim.finki.stockmap.utils.PythonExecutor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
public class PythonAnalysisController {

    @GetMapping("/analyze")
    public String analyzeData(Model model) {
        PythonExecutor.executePythonScript2("C:\\Users\\mihai\\Desktop\\StockMap\\src\\main\\java\\sentimental_analysis.py");

        List<String[]> csvData = PythonExecutor.readCsv("C:\\Users\\mihai\\Desktop\\StockMap\\src\\main\\java\\recommendationsFinal.csv");

        String classificationReport = PythonExecutor.readTextFile("C:\\Users\\mihai\\Desktop\\StockMap\\src\\main\\java\\classification_report.txt");

        model.addAttribute("csvData", csvData);
        model.addAttribute("classificationReport", classificationReport);

        return "analyze";
    }
}
