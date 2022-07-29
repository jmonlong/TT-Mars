#######################################################
echo "Inputs: "
echo "\t'\$reference': $reference"
echo "\t'\$h1': $h1"
echo "\t'\$h2': $h2"
echo "\t'\$threads': $threads"
echo "\t'\$output_dir': $output_dir"
if [ ! $ttmars_dir ]
then
    ttmars_dir='.'
fi
echo "\t'\$ttmars_dir': $ttmars_dir"
#######################################################
#1. Align assembly to reference

mkdir -p $output_dir

#use lra (https://github.com/ChaissonLab/LRA) to align asm to ref
lra index -CONTIG $reference
lra align -CONTIG $reference $h1 -t $threads -p s | samtools sort -o $output_dir/assem1_sort.bam
lra align -CONTIG $reference $h2 -t $threads -p s | samtools sort -o $output_dir/assem2_sort.bam

#index bam file
samtools index $output_dir/assem1_sort.bam
samtools index $output_dir/assem2_sort.bam

#######################################################
#######################################################
#2. Trim overlapping contigs

#trim overlapping contigs
python $ttmars_dir/trim_overlapping_contigs.py $output_dir/assem1_sort.bam $output_dir
python $ttmars_dir/trim_overlapping_contigs.py $output_dir/assem2_sort.bam $output_dir

#sort trimmed bam file
samtools sort $output_dir/assem1_sort_nool.bam -o $output_dir/assem1_nool_sort.bam
samtools sort $output_dir/assem2_sort_nool.bam -o $output_dir/assem2_nool_sort.bam

#index sorted trimmed file
samtools index $output_dir/assem1_nool_sort.bam
samtools index $output_dir/assem2_nool_sort.bam 

#######################################################
#######################################################
#3. Liftover

#convert to sam file
samtools view -h $output_dir/assem1_nool_sort.bam | samtools sort -O sam -o $output_dir/assem1_nool_sort.sam
samtools view -h $output_dir/assem2_nool_sort.bam | samtools sort -O sam -o $output_dir/assem2_nool_sort.sam

#liftover using samLiftover (https://github.com/mchaisso/mcutils): ref to asm lo
python $ttmars_dir/lo_assem_to_ref.py $output_dir $output_dir/assem1_nool_sort.bam $output_dir/assem2_nool_sort.bam

samLiftover $output_dir/assem1_nool_sort.sam $output_dir/lo_pos_assem1.bed $output_dir/lo_pos_assem1_result.bed --dir 1
samLiftover $output_dir/assem2_nool_sort.sam $output_dir/lo_pos_assem2.bed $output_dir/lo_pos_assem2_result.bed --dir 1

#liftover using samLiftover (https://github.com/mchaisso/mcutils): asm to ref lo
python $ttmars_dir/lo_assem_to_ref_0.py $output_dir $output_dir/assem1_nool_sort.bam $output_dir/assem2_nool_sort.bam

samLiftover $output_dir/assem1_nool_sort.sam $output_dir/lo_pos_assem1_0.bed $output_dir/lo_pos_assem1_0_result.bed --dir 0
samLiftover $output_dir/assem2_nool_sort.sam $output_dir/lo_pos_assem2_0.bed $output_dir/lo_pos_assem2_0_result.bed --dir 0    

#######################################################
#######################################################
#4. Compress liftover files

python $ttmars_dir/compress_liftover.py $output_dir lo_pos_assem1_result.bed lo_pos_assem1_result_compressed.bed
python $ttmars_dir/compress_liftover.py $output_dir lo_pos_assem2_result.bed lo_pos_assem2_result_compressed.bed
python $ttmars_dir/compress_liftover.py $output_dir lo_pos_assem1_0_result.bed lo_pos_assem1_0_result_compressed.bed
python $ttmars_dir/compress_liftover.py $output_dir lo_pos_assem2_0_result.bed lo_pos_assem2_0_result_compressed.bed

#######################################################
#######################################################
#5. Get non-covered regions

python $ttmars_dir/get_conf_int.py $output_dir $output_dir/assem1_nool_sort.bam $output_dir/assem2_nool_sort.bam
