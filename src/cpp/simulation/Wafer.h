#pragma once
#include <string>
#include <vector>

class Wafer {
public:
    Wafer(int id);
    void processStep(const std::string& step, double duration);
    double getYield() const;
    int getId() const;
    std::vector<std::string> getHistory() const;

private:
    int id_;
    double yield_;
    std::vector<std::string> processHistory_;
};
