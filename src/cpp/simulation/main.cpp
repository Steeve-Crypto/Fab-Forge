#include "FabSimulator.h"
#include <iostream>

int main() {
    FabSimulator sim;
    sim.runSimulation(10, 5);  // 10 wafers, 5 process steps each
    return 0;
}
