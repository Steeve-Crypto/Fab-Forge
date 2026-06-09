#include "FabSimulator.h"
#include "PLCEngine.h"
#include "EquipmentStateMachine.h"
#include <iostream>
#include <random>
#include <memory>

FabSimulator::FabSimulator() {
    addEquipment("Lithography");
    addEquipment("Etch");
    addEquipment("Deposition");
    
    // Initialize PLC and State Machines (IEC 61131-3 emulation)
    plc_ = std::make_unique<PLCEngine>();
    lithoSM_ = std::make_unique<EquipmentStateMachine>("LithographyTool");
    etchSM_ = std::make_unique<EquipmentStateMachine>("EtchTool");
    depoSM_ = std::make_unique<EquipmentStateMachine>("DepositionTool");
    
    plc_->addEquipment(lithoSM_.get());
    plc_->addEquipment(etchSM_.get());
    plc_->addEquipment(depoSM_.get());
}

void FabSimulator::addEquipment(const std::string& name) {
    equipment_.push_back(name);
}

void FabSimulator::runSimulation(int numWafers, int steps) {
    std::cout << "Starting FabForge Simulation with " << numWafers << " wafers, " << steps << " steps." << std::endl;
    
    for (int i = 0; i < numWafers; ++i) {
        wafers_.push_back(std::make_unique<Wafer>(i));
    }
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(1.0, 10.0);
    
    for (auto& wafer : wafers_) {
        for (int s = 0; s < steps; ++s) {
            std::string step = equipment_[s % equipment_.size()];
            double duration = dis(gen);
            wafer->processStep(step, duration);
            
            // PLC State Machine Sequencing (IEC 61131-3 style)
            plc_->executeLadderLogic();
            plc_->sequenceProcess(wafer->getId());
        }
    }
    
    double totalYield = 0.0;
    for (const auto& wafer : wafers_) {
        totalYield += wafer->getYield();
    }
    std::cout << "Simulation complete. Average Yield: " << (totalYield / numWafers) << std::endl;
}

std::vector<double> FabSimulator::getWaferYields() const {
    std::vector<double> yields;
    yields.reserve(wafers_.size());
    for (const auto& w : wafers_) {
        yields.push_back(w->getYield());
    }
    return yields;
}

std::vector<std::vector<std::string>> FabSimulator::getWaferHistories() const {
    std::vector<std::vector<std::string>> histories;
    histories.reserve(wafers_.size());
    for (const auto& w : wafers_) {
        histories.push_back(w->getHistory());
    }
    return histories;
}

double FabSimulator::getAverageYield() const {
    if (wafers_.empty()) return 0.0;
    double sum = 0.0;
    for (const auto& w : wafers_) sum += w->getYield();
    return sum / wafers_.size();
}
