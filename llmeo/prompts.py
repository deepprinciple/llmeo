OFF_SPRING_MAP = {
    1: "ONE",
    3: "THREE",
    5: "FIVE",
    10: "TEN",
}

PROMPT_G = (
    "I have a pool of 50 ligands in a csv file format below.\n"
    + "CSV_FILE_CONTENT"
    + "\n"
    + "This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element) that coordiate to the metal of each ligand.\n"
    + "You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n"
    + "\n"
    + "I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n"
    + "My design objective is to maximize its HOMO-LUMO gap while making the total charge of the TMC to be -1, 0 or 1.\n"
    + "All ligands in the TMC need to be those present in this csv file.\n"
    + "I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge and HOMO-LUMO gap.\n"
    + "There might be a lot of data points for TMCs being provided. Please pay attention most to TMCs those that can achieve my design objective.\n"
    + "They are provided in a format of {$TMC, ${total charge}, ${HOMO-LUMO gap}}.\n"
    + "The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n"
    + "Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n"
    + "Below are the TMCs and their ground-truth total charge and HOMO-LUMO gap.\n"
    + "CURRENT_SAMPLES"
    + "\n"
    + "Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a TMC with large HOMO-LUMO gap.\n"
    + "Then please propose NUM_SAMPLES *NEW* TMCs that have HOMO-LUMO gap larger than all the TMCs above.\n"
    + "You can make ligand crossover (i.e., swap ligands in the TMCs) and ligand mutations (i.e., substitude ligands in TMCs with thr 50 ligands in the pool) based on your knowledge to achieve the design objective.\n"
    + "If you want to be creative, you can also propose new TMCs by taking advantage of your chemistry knowledge to achieve the design objective.\n"
    + "You should make use of BOTH the groud-truth HOMO-LUMO gap data for the TMCs provided above AND your chemistry knowledge.\n"
    + "But be aware that your chemistry knowledge may be challenged in this task. When this happens, please treat the data provided as the ground truth.\n"
    + "Also please DO NOT get stuck with the existing TMCs and ligands and try to be exploratory.\n"
    + "Be sure to use the id of provided pool of 50 ligands and control the total charge of the TMC to be -1, 0, or 1, otherwise the TMC would be considered as invalid. T\n"
    + "In addition, please DO NOT propose duplicated TMCs that I have listed above.\n"
    + "\n"
    + "Your output should follow the format: {<<<Explaination>>>: $EXPLANATION, <<<TMC>>>: [$TMC],  <<<TOTAL_CHARGE>>>: ${total charge}, <<<gap>>>: $GAP}. Here are the requirements that you should fulfill:\n"
    + "1. $EXPLANATION should be your analysis about why the new TMC would have a larger HOMO-LUMO gap.\n"
    + "2. The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the center metal. $L1, $L2, $L3, and $L4 should be the id of the ligands (listed in the csv file) and follow a clockwise ordering. Please give all TMCs in a list."
    + "3. The $TMC should be valid with a total charge of -1, 0 or 1.\n"
    + "4. The $TMC should not be a duplicate of the TMCs that have been provided. If the $TMC is a duplicate, please come up with a new one instead.\n"
    + "5. $GAP is your prediction of the HOMO-LUMO gap for $TMC based on your chemistry knowledge and provided data.\n"
)

PROMPT_P = (
    "I have a pool of 50 ligands in a csv file format below.\n"
    + "CSV_FILE_CONTENT"
    + "\n"
    + "This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element) that coordiate to the metal of each ligand.\n"
    + "You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n"
    + "\n"
    + "I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n"
    + "My design objective is to maximize its polarisability while making the total charge of the TMC to be -1, 0 or 1.\n"
    + "All ligands in the TMC need to be those present in this csv file.\n"
    + "I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge and polarisability.\n"
    + "There might be a lot of data points for TMCs being provided. Please pay attention most to TMCs those that can achieve my design objective.\n"
    + "They are provided in a format of {$TMC, ${total charge}, ${polarisability}}.\n"
    + "The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n"
    + "Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n"
    + "Below are the TMCs and their ground-truth total charge and polarisability.\n"
    + "CURRENT_SAMPLES"
    + "\n"
    + "Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a TMC with large polarisability.\n"
    + "Then please propose NUM_SAMPLES *NEW* TMCs that have polarisability larger than all the TMCs above.\n"
    + "You can make ligand crossover (i.e., swap ligands in the TMCs) and ligand mutations (i.e., substitude ligands in TMCs with thr 50 ligands in the pool) based on your knowledge to achieve the design objective.\n"
    + "If you want to be creative, you can also propose new TMCs by taking advantage of your chemistry knowledge to achieve the design objective.\n"
    + "You should make use of BOTH the groud-truth polarisability data for the TMCs provided above AND your chemistry knowledge.\n"
    + "But be aware that your chemistry knowledge may be challenged in this task. When this happens, please treat the data provided as the ground truth.\n"
    + "Also please DO NOT get stuck with the existing TMCs and ligands and try to be exploratory.\n"
    + "Be sure to use the id of provided pool of 50 ligands and control the total charge of the TMC to be -1, 0, or 1, otherwise the TMC would be considered as invalid. T\n"
    + "In addition, please DO NOT propose duplicated TMCs that I have listed above.\n"
    + "\n"
    + "Your output should follow the format: {<<<Explaination>>>: $EXPLANATION, <<<TMC>>>: [$TMC],  <<<TOTAL_CHARGE>>>: ${total charge}, <<<polarisability>>>: $polarisability}. Here are the requirements that you should fulfill:\n"
    + "1. $EXPLANATION should be your analysis about why the new TMC would have a larger polarisability.\n"
    + "2. The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the center metal. $L1, $L2, $L3, and $L4 should be the id of the ligands (listed in the csv file) and follow a clockwise ordering. Please give all TMCs in a list."
    + "3. The $TMC should be valid with a total charge of -1, 0 or 1.\n"
    + "4. The $TMC should not be a duplicate of the TMCs that have been provided. If the $TMC is a duplicate, please come up with a new one instead.\n"
    + "5. $polarisability is your prediction of the polarisability for $TMC based on your chemistry knowledge and provided data.\n"
)

PROMPT_PF = (
    "I have a pool of 50 ligands in a csv file format below.\n"
    + "CSV_FILE_CONTENT"
    + "\n"
    + "This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element) that coordiate to the metal of each ligand.\n"
    + "You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n"
    + "\n"
    + "I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n"
    + "My design objective is to expand the Pareto frontier (maximizing) of my TMCs spanned by two properties, HOMO-LUMO gap and polarisability, while making the total charge of the TMC to be -1, 0 or 1.\n"
    + "All ligands in the TMC need to be those present in this csv file.\n"
    + "I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge, HOMO-LUMO gap, and polarisability.\n"
    + "There might be a lot of data points for TMCs being provided. Please pay attention most to TMCs those that can achieve my design objective.\n"
    + "They are provided in a format of {$TMC, ${total charge}, ${HOMO-LUMO gap}, $polarisability}.\n"
    + "The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n"
    + "Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n"
    + "Below are the TMCs and their ground-truth total charge, HOMO-LUMO gap, and polarisability.\n"
    + "CURRENT_SAMPLES"
    + "\n"
    + "Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a TMC lies at the Pareto frontier.\n"
    + "Then please propose NUM_SAMPLES *NEW* TMCs that further expand the Pareto frontier.\n"
    + "Be sure to have a balanced exploration of the Pareto frontier, considering those with extremely large gap and small polarisability, small gap and extremely large polarisability, and large in both gap and polarisability\n"
    + "If you find the TMCs listed above are mostly with large polarisability and small HOMO-LUMO gap, propose TMCs with large HOMO-LUMO gap, and vise versa.\n"
    + "You can make ligand crossover (i.e., swap ligands in the TMCs) and ligand mutations (i.e., substitude ligands in TMCs with thr 50 ligands in the pool) based on your knowledge to achieve the design objective.\n"
    + "If you want to be creative, you can also propose new TMCs by taking advantage of your chemistry knowledge to achieve the design objective.\n"
    + "You should make use of BOTH the groud-truth HOMO-LUMO gap and polarisability data for the TMCs provided above AND your chemistry knowledge.\n"
    + "But be aware that your chemistry knowledge may be challenged in this task. When this happens, please treat the data provided as the ground truth.\n"
    + "Also please DO NOT get stuck with the existing TMCs and ligands and try to be exploratory.\n"
    + "Be sure to use the id of provided pool of 50 ligands and control the total charge of the TMC to be -1, 0, or 1, otherwise the TMC would be considered as invalid. T\n"
    + "In addition, please DO NOT propose duplicated TMCs that I have listed above.\n"
    + "\n"
    + "Your output should follow the format: {<<<Explaination>>>: $EXPLANATION, <<<TMC>>>: [$TMC],  <<<TOTAL_CHARGE>>>: ${total charge}, <<<gap>>>: $GAP, <<<polarisability>>>: $polarisability}. Here are the requirements that you should fulfill:\n"
    + "1. $EXPLANATION should be your analysis about why the new TMC would have a larger HOMO-LUMO gap.\n"
    + "2. The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the center metal. $L1, $L2, $L3, and $L4 should be the id of the ligands (listed in the csv file) and follow a clockwise ordering. Please give all TMCs in a list.\n"
    + "3. The $TMC should be valid with a total charge of -1, 0 or 1.\n"
    + "4. The $TMC should not be a duplicate of the TMCs that have been provided. If the $TMC is a duplicate, please come up with a new one instead.\n"
    + "5. $GAP is your prediction of the HOMO-LUMO gap for $TMC based on your chemistry knowledge and provided data.\n"
    + "5. $polarisability is your prediction of the polarisability for $TMC based on your chemistry knowledge and provided data.\n"
)


PROMPT_MB = (
    "I have a pool of 50 ligands in a csv file format below.\n"
    + "CSV_FILE_CONTENT"
    + "\n"
    + "This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element) that coordiate to the metal of each ligand.\n"
    + "You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n"
    + "\n"
    + "I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n"
    + "My design objective is to find TMCs that simultaneously maximize both HOMO-LUMO gap (> 4 eV) and polarisability (> 400 au), potentially by maximizing their mutiplication, while making the total charge of the TMC to be -1, 0 or 1.\n"
    + "At least give me TMCs with HOMO-LUMO gap > 4 eV and polarisability > 400 au. All ligands in the TMC need to be those present in this csv file.\n"
    + "I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge, HOMO-LUMO gap, and polarisability.\n"
    + "There might be a lot of data points for TMCs being provided. Please pay attention most to TMCs those that can achieve my design objective.\n"
    + "They are provided in a format of {$TMC, ${total charge}, ${HOMO-LUMO gap}, $polarisability}.\n"
    + "The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n"
    + "Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n"
    + "Below are the TMCs and their ground-truth total charge, HOMO-LUMO gap, and polarisability.\n"
    + "CURRENT_SAMPLES"
    + "\n"
    + "Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a TMC have both extremely large HOMO-LUMO gap and polarisability.\n"
    + "Then please propose NUM_SAMPLES *NEW* TMCs that further maximize these two properties at the same time, potentially by maximizing their mutiplication.\n"
    + "If you find the TMCs listed above have extremely large polarisability (> 450 au) but small HOMO-LUMO gap (< 2 eV), propose more TMCs with larger HOMO-LUMO gap while maintaining their polarisability.\n"
    + "In contrast, if you find the TMCs have extremely small polarisability (< 250 au) but large HOMO-LUMO gap (> 4.5 eV), propose more TMCs with larger polarisability while maintaining their HOMO-LUMO gap.\n"
    + "You can make ligand crossover (i.e., swap ligands in the TMCs) and ligand mutations (i.e., substitude ligands in TMCs with thr 50 ligands in the pool) based on your knowledge to achieve the design objective.\n"
    + "If you want to be creative, you can also propose new TMCs by taking advantage of your chemistry knowledge to achieve the design objective.\n"
    + "You should make use of BOTH the groud-truth HOMO-LUMO gap and polarisability data for the TMCs provided above AND your chemistry knowledge.\n"
    + "But be aware that your chemistry knowledge may be challenged in this task. When this happens, please treat the data provided as the ground truth.\n"
    + "Also please DO NOT get stuck with the existing TMCs and ligands and try to be exploratory.\n"
    + "Be sure to use the id of provided pool of 50 ligands and control the total charge of the TMC to be -1, 0, or 1, otherwise the TMC would be considered as invalid. T\n"
    + "In addition, please DO NOT propose duplicated TMCs that I have listed above.\n"
    + "\n"
    + "Your output should follow the format: {<<<Explaination>>>: $EXPLANATION, <<<TMC>>>: [$TMC],  <<<TOTAL_CHARGE>>>: ${total charge}, <<<gap>>>: $GAP, <<<polarisability>>>: $polarisability}. Here are the requirements that you should fulfill:\n"
    + "1. $EXPLANATION should be your analysis grounded on chemistry knowledge and provided data about why the new TMC would have extremely large HOMO-LUMO gap and polarisability.\n"
    + "2. The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the center metal. $L1, $L2, $L3, and $L4 should be the id of the ligands (listed in the csv file) and follow a clockwise ordering. Please give all TMCs in a list.\n"
    + "3. The $TMC should be valid with a total charge of -1, 0 or 1.\n"
    + "4. The $TMC should not be a duplicate of the TMCs that have been provided. If the $TMC is a duplicate, please come up with a new one instead.\n"
    + "5. $GAP is your prediction of the HOMO-LUMO gap for $TMC based on your chemistry knowledge and provided data.\n"
    + "6. $polarisability is your prediction of the polarisability for $TMC based on your chemistry knowledge and provided data.\n"
)


PROMPT_MPSG = (
    "I have a pool of 50 ligands in a csv file format below.\n"
    + "CSV_FILE_CONTENT"
    + "\n"
    + "This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element) that coordiate to the metal of each ligand.\n"
    + "You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n"
    + "\n"
    + "I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n"
    + "My design objective is to design TMCs with maximized polarisability (> 450 au) and minimized HOMO-LUMO gap (< 0.5 eV), while making the total charge of the TMC to be -1, 0 or 1\n"
    + "All ligands in the TMC need to be those present in this csv file.\n"
    + "I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge, HOMO-LUMO gap, and polarisability.\n"
    + "There might be a lot of data points for TMCs being provided. Please pay attention most to TMCs that can best achieve my design objective.\n"
    + "They are provided in a format of {$TMC, ${total charge}, ${HOMO-LUMO gap}, $polarisability}.\n"
    + "The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n"
    + "Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n"
    + "Below are the TMCs and their ground-truth total charge, HOMO-LUMO gap, and polarisability.\n"
    + "CURRENT_SAMPLES"
    + "\n"
    + "Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a TMC have extremely large polarisability while matainining a extremely small HOMO-LUMO gap.\n"
    + "Then please propose NUM_SAMPLES *NEW* TMCs that further maximize the polarisabilty while minimizing the HOMO-LUMO gap.\n"
    + "If you find the TMCs listed above have extremely large polarisability (> 450 au) but still have large HOMO-LUMO gap (> 1.0 eV), propose more TMCs with smaller HOMO-LUMO gap while maintaining their large polarisability.\n"
    + "In contrast, if you find the TMCs have extremely small polarisability (< 300 au) but also small HOMO-LUMO gap (< 0.5 eV), propose more TMCs with larger polarisability while maintaining their small HOMO-LUMO gap.\n"
    + "You can make ligand crossover (i.e., swap ligands in the TMCs) and ligand mutations (i.e., substitude ligands in TMCs with the 50 ligands in the pool) based on your knowledge to achieve the design objective.\n"
    + "If you want to be creative, you can also propose new TMCs by taking advantage of your chemistry knowledge to achieve the design objective.\n"
    + "You should make use of BOTH the groud-truth HOMO-LUMO gap and polarisability data for the TMCs provided above AND your chemistry knowledge.\n"
    + "But be aware that your chemistry knowledge may be challenged in this task. When this happens, please treat the data provided as the ground truth.\n"
    + "Also please DO NOT get stuck with the existing TMCs and ligands and try to be exploratory.\n"
    + "Be sure to use the id of provided pool of 50 ligands and control the total charge of the TMC to be -1, 0, or 1, otherwise the TMC would be considered as invalid. T\n"
    + "In addition, please DO NOT propose duplicated TMCs that I have listed above.\n"
    + "\n"
    + "Your output should follow the format: {<<<Explaination>>>: $EXPLANATION, <<<TMC>>>: [$TMC],  <<<TOTAL_CHARGE>>>: ${total charge}, <<<gap>>>: $GAP, <<<polarisability>>>: $polarisability}. Here are the requirements that you should fulfill:\n"
    + "1. $EXPLANATION should be your analysis grounded on chemistry knowledge and provided data about why the new TMC would have extremely large polarisability and extremely small HOMO-LUMO gap.\n"
    + "2. The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the center metal. $L1, $L2, $L3, and $L4 should be the id of the ligands (listed in the csv file) and follow a clockwise ordering. Please give all TMCs in a list.\n"
    + "3. The $TMC should be valid with a total charge of -1, 0 or 1.\n"
    + "4. The $TMC should not be a duplicate of the TMCs that have been provided. If the $TMC is a duplicate, please come up with a new one instead.\n"
    + "5. $GAP is your prediction of the HOMO-LUMO gap for $TMC based on your chemistry knowledge and provided data.\n"
    + "6. $polarisability is your prediction of the polarisability for $TMC based on your chemistry knowledge and provided data.\n"
)

PROMPT_NL_MB = (
    "I have a pool of 50 ligands in a csv file format below.\n"
    + "CSV_FILE_CONTENT"
    + "\n"
    + "This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element, for example, N, 2 means the second N atom in the SMILES string, NOT the absolute index) that coordiate to the metal of each ligand.\n"
    + "You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n"
    + "\n"
    + "I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n"
    + "My design objective is to maximize both its polarisability and its HOMO-LUMO gap, potentially by maximizing their multiplication, while making the total charge of the TMC to be -1, 0 or 1.\n"
    + "I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge and polarisability.\n"
    + "They are provided in a format of {$TMC, ${total charge}, ${HOMO-LUMO gap}, ${polarisability}}.\n"
    + "The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n"
    + "Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n"
    + "Below are the TMCs and their ground-truth total charge, HOMO-LUMO gap, and polarisability.\n"
    + "CURRENT_SAMPLES"
    + "\n"
    + "Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a ligand combination give extremely large polarisability and HOMO-LUMO gap for a Pd(II) square planar TMC.\n"
    + "Then based on your chemistry knowledge and NUM_PROVIDED_SAMPLES example TMCs provided, can you give me 10 NEW ligands that would help me further maximize the polarisability and HOMO-LUMO gap when they are coordinated to Pd(II) and form a square planar TMC?\n"
    + "For the 10 new ligands, I would like 5 of them being neutral and 5 of them being anionic. It would be best for them to be monodentate (that is, only one atom coordinating to the metal).\n"
    + "Please give me these 10 new ligands in the same format as the 50 original ligands I provided in the beigining. For the id, please follow the format of <SIX-upper-letter>-subgraph-<integter>.\n"
    + "These 10 new ligands should NOT be duplicates of what are originally provided in the 50 ligands pool. Please double check the SMILES string before you hand me back the 10 new ligands. In addition, please only use C, N, O, P, and S as connecting atoms.\n"
)

PROMPT_Unbounded_P =  "I have a pool of 50 ligands in a csv file format below.\n" + \
"CSV_FILE_CONTENT" + \
"\n"+ \
"This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element, for example, N, 2 means the second N atom in the SMILES string) that coordiate to the metal of each ligand.\n" + \
"You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n" + \
"\n" + \
"I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n" + \
"My design objective is to maximize its polarisability while making the total charge of the TMC to be -1, 0 or 1.\n" + \
"I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge and polarisability.\n" + \
"They are provided in a format of {$TMC, ${total charge}, ${polarisability}}.\n"  + \
"The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n" + \
"Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n" + \
"Below are the TMCs and their ground-truth total charge and polarisability.\n" + \
"CURRENT_SAMPLES" + \
"\n"+ \
"Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a ligand combination give extremely large polarisability for a TMC.\n" + \
"Then based on your chemistry knowledge and NUM_PROVIDED_SAMPLES example TMCs provided, can you give me TEN new TMCs that would help me further maximize the polarisability?\n"+ \
"For the TEN proposed TMCs, you must need to design new ligands to achieve the objective. Ensure that there are more than one ligands being outside of the given ligands pool. In addition, please only use C, N, O, P, and S as connecting atoms.\n"+ \
"Note that the Pd atom has a +2 charge, so the summation of charge for the 4 ligands needs to be -3, -2, or -1. \n"+ \
"For each TMC, please write down their four consisting ligands following the format of initial ligand list (with id named as <six-upper-letter>-subgraph-<integter>), no matter whether a ligand is newly designed or in the initial 50 ligand list.\n"+ \
"Please make sure you use SIX upper letter (instead of other number) as part of the ligand id. For each ligand, please additionally note down whether they are in the initial 50 ligands list.\n"+ \
"When you return the results, please treat these TEN proposed TMCs independent. In this case, describe the ligands for each TMC in details despite they have been used in other TMCs.\n" + \
"Your output should follow the format: {<<<Explaination>>>: $EXPLANATION, <<<TMC>>>: $TMC, <<<CHARGE>>>: $charge}. Here are the requirements that you should fulfill:\n" + \
"1. $EXPLANATION should be your analysis about why the new TMC would result a larger polarisability.\n" + \
"2. $TMC should follow the format of NUM_PROVIDED_SAMPLES TMCs that I listed above. With the name of TMC, its total charge, and your prediction of its polarisability.\n" + \
"3. Please give me the full details of all four ligands in each TMC despite they are in the initial 50 ligands list or have been used in other TMCs. \n"+\
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"5. $charge is the total charge of the TMC. Please show me the detailed calculation process. Note $charge needs to be -1, 0, or 1.\n" + \
"6. do not give any additional infomation that are not listed in below example"+\
"7. if you see any words in the error section of the provided TMCs, please think also think about how to avoid them when you provide new TMCs"+\
"\n"+ \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"\n"+ \
"Below is an example: \n"+ \
"{\n"+ \
"<<<Explanation>>>: By combining two anionic ligands with extensive conjugation (BIFZEX-subgraph-0 and REBWEB-subgraph-2) and two bulky neutral ligands (CUJYEL-subgraph-2 and LETTEL-subgraph-1), the complex may achieve higher polarizability. The anionic ligands contribute significant electron density, and the neutral ligands enhance the electron cloud's size and flexibility.\n"+ \
 "<<<TMC>>>: {Pd_ULUSIE-subgraph-1_MAQKEX-subgraph-1_PERFPU-subgraph-1_TFMETH-subgraph-1, charge = -1, polarisability = 500.0}\n"+ \
 "<<<CHARGE>>>: +2 + 0 - 1 - 1 - 1 = -1. Within the range of -1, 0, or 1. \n"+ \
 "**Ligand Details**:\n"+ \
"\n"+ \
 "1. **ULUSIE-subgraph-1** (In initial 50 ligands)\n"+ \
 "   - SMILES: N\n"+ \
 "   - id: ULUSIE-subgraph-1\n"+ \
 "   - charge: 0\n"+ \
 "   - connecting atom element: N\n"+ \
 "   - connecting atom index: 1\n"+ \
 "\n"+ \
 "2. **MAQKEX-subgraph-1** (In initial 50 ligands)\n"+ \
 "   - SMILES: [C-](F)(F)F\n"+ \
 "   - id: MAQKEX-subgraph-1\n"+ \
 "   - charge: -1\n"+ \
 "   - connecting atom element: C\n"+ \
 "   - connecting atom index: 1\n"+ \
 "\n"+ \
 "3. **PERFPU-subgraph-1** (New ligand, not in initial 50 ligands)\n"+ \
 "   - SMILES: [c-]1c(c(c(c(c1F)F)F)F)F\n"+ \
 "   - id: PERFPU-subgraph-1\n"+ \
 "   - charge: -1\n"+ \
 "   - connecting atom element: C\n"+ \
 "   - connecting atom index: 1\n"+ \
 "\n"+ \
 "4. **TFMETH-subgraph-1** (New ligand, not in initial 50 ligands)\n"+ \
 "   - SMILES: [O-]C(F)(F)F\n"+ \
 "   - id: TFMETH-subgraph-1\n"+ \
 "   - charge: -1\n"+ \
 "   - connecting atom element: O\n"+ \
 "   - connecting atom index: 1\n"+ \
 "}\n"+ \
"----\n"

PROMPT_Unbounded_Both =  "I have a pool of 50 ligands in a csv file format below.\n" + \
"CSV_FILE_CONTENT" + \
"\n"+ \
"This csv files contains the SMILES string, id, charge, and the connecting atoms and index (corresponding to the occurrance of the connecting element, for example, N, 2 means the second N atom in the SMILES string) that coordiate to the metal of each ligand.\n" + \
"You will use this pool of ligands frequently. Please remember the correspondence between their SMILES string, id, charge, and connecting atom element.\n" + \
"\n" + \
"I am interested in making a Pd based square planer transition metal complex (TMC) with Pd in +2 oxidation state.\n" + \
"My design objective is to simultaneously maximize its polarisability and homo-lumo gap while making the total charge of the TMC to be -1, 0 or 1.\n" + \
"I have made NUM_PROVIDED_SAMPLES TMCs and measured their total charge, polarisability, and homo-lumo gap.\n" + \
"They are provided in a format of {$TMC, ${total charge}, ${polarisability}, ${homo-lumo gap}, {error message(if any)}}.\n"  + \
"The $TMC should be in a format of Pd_$L1_$L2_$L3_$L4, where Pd is the metal center , $L1, $L2, $L3, and $L4 are the id of the ligands (listed in the csv file) and follow a clockwise ordering.\n" + \
"Note that the $TMC has cyclic symmetry for the ligands so that Pd_$L1_$L2_$L3_$L4, Pd_$L2_$L3_$L4_$L1, Pd_$L3_$L4_$L1_$L2, and Pd_$L4_$L1_$L2_$L3 are the same TMC.\n" + \
"Below are the TMCs and their ground-truth total charge and polarisability, and homo-lumo gap.\n" + \
"CURRENT_SAMPLES" + \
"\n"+ \
"Grounded on your chemistry knowledge, look at the pattern of the provided data and think about what makes a ligand combination give extremely large polarisability and extremely large homo-lumo gap for a TMC.\n" + \
"Then based on your chemistry knowledge and NUM_PROVIDED_SAMPLES example TMCs provided, can you give me TEN new TMCs that would help me further maximize the polarisability (> 450 au) and homo-lumo gap (> 4.5 eV) ?\n"+ \
"I am expecting that the new proposed TMC has a larger Homo-lumo gap, and also a larger polarisability than the largest in given TMCs. \n"+\
"For the TEN proposed TMCs, you must need to design new ligands to achieve the objective. Ensure that there are at least one ligands being outside of the given ligands pool. In addition, please only use C, N, O, P, and S as connecting atoms.\n"+ \
"Note that the Pd atom has a +2 charge, so the summation of charge for the 4 ligands needs to be -3, -2, or -1. Also, maximizing homo-lumo gap is as important as maximizing polarisability. \n"+ \
"For each TMC, please write down their four consisting ligands following the format of initial ligand list (with id named as <six-upper-letter>-subgraph-<integter>), no matter whether a ligand is newly designed or in the initial 50 ligand list.\n"+ \
"Please make sure you use SIX upper letter (instead of other number) as part of the ligand id. For each ligand, please additionally note down whether they are in the initial 50 ligands list.\n"+ \
"When you return the results, please treat these TEN proposed TMCs independent. In this case, describe the ligands for each TMC in details despite they have been used in other TMCs.\n" + \
"Your output should follow the format: {<<<Explaination>>>: $EXPLANATION, <<<TMC>>>: $TMC, <<<CHARGE>>>: $charge}. Here are the requirements that you should fulfill:\n" + \
"1. $EXPLANATION should be your analysis about why the new TMC would result a larger polarisability and homo-lumo gap.\n" + \
"2. $TMC should follow the format of NUM_PROVIDED_SAMPLES TMCs that I listed above. With the name of TMC, its total charge, and your prediction of its polarisability and homo-lumo gap.\n" + \
"3. Please give me the full details of all four ligands in each TMC despite they are in the initial 50 ligands list or have been used in other TMCs. \n"+\
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"5. $charge is the total charge of the TMC. Please show me the detailed calculation process. Note $charge needs to be -1, 0, or 1.\n" + \
"6. do not give any additional infomation that are not listed in below example"+\
"7. if you see any words in the error section of the provided TMCs, please think also think about how to avoid them when you provide new TMCs"+\
"\n"+ \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"4. DO NOT just tell me \"same as above\" when you give me ligand details if even the same information will appear.\n" + \
"\n"+ \
"Below is an example: \n"+ \
"{\n"+ \
"<<<Explanation>>>: By combining two anionic ligands with extensive conjugation (BIFZEX-subgraph-0 and REBWEB-subgraph-2) and two bulky neutral ligands (CUJYEL-subgraph-2 and LETTEL-subgraph-1), the complex may achieve higher polarizability. The anionic ligands contribute significant electron density, and the neutral ligands enhance the electron cloud's size and flexibility. The strong electron-withdrawing effects of the fluorinated ligands, which stabilize the HOMO and raise the LUMO, leading to a larger energy separation. \n"+ \
 "<<<TMC>>>: {Pd_ULUSIE-subgraph-1_MAQKEX-subgraph-1_PERFPU-subgraph-1_TFMETH-subgraph-1, charge = -1, polarisability = 500.0, homo-lumo gap = 2.75}\n"+ \
 "<<<CHARGE>>>: +2 + 0 - 1 - 1 - 1 = -1. Within the range of -1, 0, or 1. \n"+ \
 "**Ligand Details**:\n"+ \
"\n"+ \
 "1. **ULUSIE-subgraph-1** (In initial 50 ligands)\n"+ \
 "   - SMILES: N\n"+ \
 "   - id: ULUSIE-subgraph-1\n"+ \
 "   - charge: 0\n"+ \
 "   - connecting atom element: N\n"+ \
 "   - connecting atom index: 1\n"+ \
 "\n"+ \
 "2. **MAQKEX-subgraph-1** (In initial 50 ligands)\n"+ \
 "   - SMILES: [C-](F)(F)F\n"+ \
 "   - id: MAQKEX-subgraph-1\n"+ \
 "   - charge: -1\n"+ \
 "   - connecting atom element: C\n"+ \
 "   - connecting atom index: 1\n"+ \
 "\n"+ \
 "3. **PERFPU-subgraph-1** (New ligand, not in initial 50 ligands)\n"+ \
 "   - SMILES: [c-]1c(c(c(c(c1F)F)F)F)F\n"+ \
 "   - id: PERFPU-subgraph-1\n"+ \
 "   - charge: -1\n"+ \
 "   - connecting atom element: C\n"+ \
 "   - connecting atom index: 1\n"+ \
 "\n"+ \
 "4. **TFMETH-subgraph-1** (New ligand, not in initial 50 ligands)\n"+ \
 "   - SMILES: [O-]C(F)(F)F\n"+ \
 "   - id: TFMETH-subgraph-1\n"+ \
 "   - charge: -1\n"+ \
 "   - connecting atom element: O\n"+ \
 "   - connecting atom index: 1\n"+ \
 "}\n"+ \
"----\n"
