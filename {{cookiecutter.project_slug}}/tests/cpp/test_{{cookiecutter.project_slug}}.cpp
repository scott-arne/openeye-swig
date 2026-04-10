#include <gtest/gtest.h>

#include "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}.h"

#include <oechem.h>

namespace {{ cookiecutter.project_prefix }} {
namespace test {

class MolecularWeightTest : public ::testing::Test {
protected:
    OEChem::OEGraphMol mol_;
};

TEST_F(MolecularWeightTest, Aspirin) {
    OEChem::OESmilesToMol(mol_, "CC(=O)OC1=CC=CC=C1C(=O)O");
    double mw = calculate_molecular_weight(mol_);
    EXPECT_NEAR(mw, 180.157, 0.01);
}

TEST_F(MolecularWeightTest, Ethanol) {
    OEChem::OESmilesToMol(mol_, "CCO");
    double mw = calculate_molecular_weight(mol_);
    EXPECT_NEAR(mw, 46.069, 0.01);
}

TEST_F(MolecularWeightTest, ReturnsPositiveValue) {
    OEChem::OESmilesToMol(mol_, "C");
    double mw = calculate_molecular_weight(mol_);
    EXPECT_GT(mw, 0.0);
}

TEST(VersionTest, MacrosDefined) {
    EXPECT_GE({{ cookiecutter.project_prefix }}_VERSION_MAJOR, 0);
    EXPECT_GE({{ cookiecutter.project_prefix }}_VERSION_MINOR, 0);
    EXPECT_GE({{ cookiecutter.project_prefix }}_VERSION_PATCH, 0);
}

} // namespace test
} // namespace {{ cookiecutter.project_prefix }}
