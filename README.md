# TT-Mars

TT-Mars: S**t**ructural Varian**t**s Assess**m**ent B**a**sed on Haplotype-**r**esolved A**s**semblies.

## Disclaimer

**This is a tweaked version of the official TT-Mars (https://github.com/ChaissonLab/TT-Mars)**.

I made a few changes to help our use cases and to simplify the pipelining:
- no need to specify if we use "hg38" anymore. The chromosome names are guessed from the reference fasta file. Of note, it won't use all the chromosome in the fasta file. It's still looking for just the autosomes and sex chromosomes in case it is important to not include the alt contigs (maybe for the alignment step, or the definition of duplications?).
- the chromosome lengths are not (approximatively) hard-coded anymore. This should help being more robust, esp. when using non-hg19/hg38 references, e.g. CHM13.
- chromosome names in the centromere file are consistent with other files. It used to be that the centromere file had the 'chr' prefix no matter what.
- To make it easy to parralelize TT-Mars I added a new (optional) argument (`-c/--chrs`) to specify a subset of chromosomes to analyze.

Note: I just realized the tandem repeats must be either sorted or at least grouped by chromosome in the tandem repeat file.

## Usage

0. Clone TT-Mars from github and `cd TT-Mars`.
1. Create environment and activate: `conda create -n ttmars` and `conda activate ttmars_test`.
2. Run `dowaload_files.sh` to download required files to `./ttmars_files`.
3. Run `download_asm.sh` to download assembly files of 10 samples from HGSVC.
4. Install packages: `conda install -c bioconda pysam`, `conda install -c anaconda numpy`, `conda install -c bioconda mappy`, `conda install -c conda-forge biopython`, `conda install -c bioconda pybedtools`.
5. Run TT-Mars with following steps: `run_ttmars.sh` includes more instructions. Users can run it to run TT-Mars after setting up.

The main program:  

`python ttmars.py output_dir centro_file files_dir/assem1_non_cov_regions.bed files_dir/assem2_non_cov_regions.bed vcf_file reference asm_h1 asm_h2 files_dir/lo_pos_assem1_result_compressed.bed files_dir/lo_pos_assem2_result_compressed.bed files_dir/lo_pos_assem1_0_result_compressed.bed files_dir/lo_pos_assem2_0_result_compressed.bed tr_file`

Script to combine results and output:  

`python combine.py output_dir num_X_chr`

## Positional arguments

1. `output_dir`: Output directory.
2. `centro_file`: provided centromere file. 
3. `tr_file`: provided tandem repeats file.
4. `vcf_file`: callset file callset.vcf(.gz)  
5. `reference`: referemce file reference_genome.fasta.
6. `asm_h1/2`: assembly files assembly1/2.fa, can be downloaded by `download_asm.sh`.
7. `assem1_non_cov_regions.bed`, `assem2_non_cov_regions.bed`, `lo_pos_assem1_result_compressed.bed`, `lo_pos_assem2_result_compressed.bed`, `lo_pos_assem1_0_result_compressed.bed`, `lo_pos_assem2_0_result_compressed.bed`: required files, downloaded to `./ttmars_files`.
8. `num_X_chr`: if male sample: 1; if female sample: 2.

## Optional arguments

1. ttmars.py:  
`-n/--not_hg38`: if reference is NOT hg38 (hg19).  
`-p/--passonly`: if consider PASS calls only.   
`-s/--seq_resolved`: if consider sequence resolved calls (INS).  
`-w/--wrong_len`: if count wrong length calls as True.  
`-g/--gt_vali`: conduct genotype validation.  
`-c/--chrs`: subset of chromosomes to analyze (separated by `,`)

2. combine.py:  
`-v/--vcf_out`: output results as vcf files (tp (true positive), fp (false positive) and na), must be used together with `-f/--vcf_file`.  
`-f VCF_FILE/--vcf_file VCF_FILE`: input vcf file, use as template.  
`-g/--gt_vali`: conduct genotype validation.  
`-n/--false_neg`: output recall, must be used together with `-t/--truth_file` and `-f/--vcf_file`.  
`-t/--truth_file`: input truth vcf file, must be used together with `-n/--false_neg`.  

## Example Output

ttmars_combined_res.txt:  
|chr| start| end| type| relative length| relative score| validation result| genotype match|
| :----: | :----: |  :----: | :----: | :----: | :----: | :----: |:----: | 
|chr1|	893792|	893827|	DEL|	1.03|	3.18|	True| True|

## Accompanying Resources

### Liftover files  
| Samples      | Reference Liftover Hap1 | Reference Liftover Hap2 | Assembly Liftover Hap1 | Assembly Liftover Hap2 |
| :----:      |    :----:   |        :----: |    :----:   |        :----: |
| HG00096 | https://figshare.com/ndownloader/files/30817390 | https://figshare.com/ndownloader/files/30817384 | https://figshare.com/ndownloader/files/30817387  |  https://figshare.com/ndownloader/files/30817381   |
| HG00171 | https://figshare.com/ndownloader/files/30817402  | https://figshare.com/ndownloader/files/30817396 |  https://figshare.com/ndownloader/files/30817399 |  https://figshare.com/ndownloader/files/30817393    |
| HG00513 | https://figshare.com/ndownloader/files/30817411  | https://figshare.com/ndownloader/files/30817405 | https://figshare.com/ndownloader/files/30817408  |   https://figshare.com/ndownloader/files/30817414   |
| HG00731 |  https://figshare.com/ndownloader/files/30817426 | https://figshare.com/ndownloader/files/30817420 | https://figshare.com/ndownloader/files/30817423  |  https://figshare.com/ndownloader/files/30817417    |
| HG00732 |  https://figshare.com/ndownloader/files/30817435 | https://figshare.com/ndownloader/files/30817429 | https://figshare.com/ndownloader/files/30817432  |   https://figshare.com/ndownloader/files/30817438   |
| HG00864 |  https://figshare.com/ndownloader/files/30817450 | https://figshare.com/ndownloader/files/30817444 | https://figshare.com/ndownloader/files/30817447  |   https://figshare.com/ndownloader/files/30817441   |
| HG01114 |  https://figshare.com/ndownloader/files/30817459 | https://figshare.com/ndownloader/files/30817453 |  https://figshare.com/ndownloader/files/30817456 |   https://figshare.com/ndownloader/files/30817462   |
| HG01505 | https://figshare.com/ndownloader/files/30817471  | https://figshare.com/ndownloader/files/30817465 | https://figshare.com/ndownloader/files/30817468  |   https://figshare.com/ndownloader/files/30817474   |
| HG01596 |  https://figshare.com/ndownloader/files/30817486 | https://figshare.com/ndownloader/files/30817480 | https://figshare.com/ndownloader/files/30817483  |   https://figshare.com/ndownloader/files/30817477   |
| HG03009 | https://figshare.com/ndownloader/files/30817498 | https://figshare.com/ndownloader/files/30817492 |  https://figshare.com/ndownloader/files/30817495 |   https://figshare.com/ndownloader/files/30817489   |
| HG002 (hg19 ref) | https://figshare.com/ndownloader/files/31455682 | https://figshare.com/ndownloader/files/31455676 |  https://figshare.com/ndownloader/files/31455685 |   https://figshare.com/ndownloader/files/31455679   |


### Genome coverage files  
| Samples      | Hap1 | Hap2 |
| :----:      |    :----:   |        :----: |
| HG00096 | https://figshare.com/ndownloader/files/30850246 | https://figshare.com/ndownloader/files/30850249 |
| HG00171 | https://figshare.com/ndownloader/files/30850258 | https://figshare.com/ndownloader/files/30850261 |
| HG00513 | https://figshare.com/ndownloader/files/30850639 | https://figshare.com/ndownloader/files/30850642 | 
| HG00731 |  https://figshare.com/ndownloader/files/30850663 | https://figshare.com/ndownloader/files/30850660 | 
| HG00732 | https://figshare.com/ndownloader/files/30850687 | https://figshare.com/ndownloader/files/30850681 |
| HG00864 | https://figshare.com/ndownloader/files/30850708 | https://figshare.com/ndownloader/files/30850711 | 
| HG01114 | https://figshare.com/ndownloader/files/30850726 | https://figshare.com/ndownloader/files/30850729 | 
| HG01505 | https://figshare.com/ndownloader/files/30850747  | https://figshare.com/ndownloader/files/30850744 | 
| HG01596 | https://figshare.com/ndownloader/files/30850768 | https://figshare.com/ndownloader/files/30850762 |
| HG03009 | https://figshare.com/ndownloader/files/30850777 | https://figshare.com/ndownloader/files/30850780 | 
| HG002 (hg19 ref) | https://figshare.com/ndownloader/files/31455670 | https://figshare.com/ndownloader/files/31455673 | 
