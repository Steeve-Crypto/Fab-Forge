#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "FabSimulator.h"
#include "Wafer.h"
#include "PLCEngine.h"
#include "EquipmentStateMachine.h"

namespace py = pybind11;

PYBIND11_MODULE(fabforge_cpp, m) {
    m.doc() = "FabForge C++ core with PyBind11 bindings";

    py::class_<Wafer>(m, "Wafer")
        .def(py::init<int>())
        .def("get_id", &Wafer::getId)
        .def("process_step", &Wafer::processStep)
        .def("get_yield", &Wafer::getYield)
        .def("get_history", &Wafer::getHistory);

    py::class_<FabSimulator>(m, "FabSimulator")
        .def(py::init<>())
        .def("run_simulation", &FabSimulator::runSimulation)
        .def("add_equipment", &FabSimulator::addEquipment)
        .def("get_wafer_yields", &FabSimulator::getWaferYields)
        .def("get_wafer_histories", &FabSimulator::getWaferHistories)
        .def("get_average_yield", &FabSimulator::getAverageYield);

    // PLC and StateMachine (with compatibility names)
    py::class_<PLCEngine>(m, "PLCEngine")
        .def(py::init<>())
        .def("execute_rung", &PLCEngine::executeRung)
        .def("execute_ladder", &PLCEngine::executeLadderLogic);

    py::class_<EquipmentStateMachine>(m, "EquipmentStateMachine")
        .def(py::init<const std::string&>())
        .def("transition_to", &EquipmentStateMachine::transitionTo)
        .def("transition", &EquipmentStateMachine::transition)
        .def("get_current_state", &EquipmentStateMachine::getCurrentState)
        .def("get_status", &EquipmentStateMachine::getStatus)
        .def("process_wafer", &EquipmentStateMachine::processWafer);
}
