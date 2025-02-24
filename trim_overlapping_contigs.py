import pysam
import sys 
import os
import csv
#import copy

#input: input bam file (sorted bam), output directory
#output: output directory/output bam file (unsorted)

file_name = sys.argv[1]
infile = pysam.AlignmentFile(file_name, "rb")
#file not sorted

#outfile_name = "mm2_hg38_asm5_woSed_assem2_nool.bam"
#outfile_name = sys.argv[2]

infile_name_base=os.path.basename(file_name)
outfile_name_wo_ext = os.path.splitext(infile_name_base)[0]

outfile_name = outfile_name_wo_ext + "_nool.bam"

#output_dir = "assemblies/HG00096"
output_dir = sys.argv[2] + "/"

outfile = pysam.AlignmentFile(output_dir + outfile_name, "wb", template=infile)

#sort contigs by length from short to long
def mergesort_contigs(unsorted_list):
    if len(unsorted_list) > 1:
        #floor division
        mid = len(unsorted_list)//2
        #Divide
        L_list = unsorted_list[:mid]
        R_list = unsorted_list[mid:]
        #Conquer
        mergesort_contigs(L_list)
        mergesort_contigs(R_list)
        #Merge
        i = j = k = 0
        while i < len(L_list) and j < len(R_list):
            if L_list[i].query_alignment_length < R_list[j].query_alignment_length:
                unsorted_list[k] = L_list[i]
                i += 1
            else:
                unsorted_list[k] = R_list[j]
                j += 1
            k += 1
        
        while i < len(L_list):
            unsorted_list[k] = L_list[i]
            i += 1
            k += 1
            
        while j < len(R_list):
            unsorted_list[k] = R_list[j]
            j += 1
            k += 1 
            
            
def find_query_pos(contig, ref_pos):
    #note -1?
    cur_contig_pos = contig.query_alignment_start
    cur_ref_pos = contig.reference_start
    cigar_tuples = contig.cigartuples
    
    #here3 [(4, 1), (0, 1195), (5, 239224)]
    #here4 197757984 197756789 197757984
    #test
    #print("here4", ref_pos, contig.reference_start, contig.reference_end)
    #bad input ref_pos
    if ref_pos < contig.reference_start or ref_pos > contig.reference_end:
        return -1
    #loop through cigar tuples
    for tup in cigar_tuples:
        
        #if softclip
#         if tup[0] == 4:
#             #or skip this tuple: we had cur_contig_pos = contig.query_alignment_start
#             cur_contig_pos = tup[1] - 1
#             continue

        #if tup consumes both contig and ref, and reached the target ref_pos
        if tup[0] in [0, 7, 8] and cur_ref_pos < ref_pos and cur_ref_pos + tup[1] >= ref_pos:
            return cur_contig_pos + (ref_pos - cur_ref_pos)
        #elif tup consemes ref only, and reached the target ref_pos
        elif tup[0] in [2, 3] and cur_ref_pos < ref_pos and cur_ref_pos + tup[1] >= ref_pos:
            return cur_contig_pos
        #if consume contig, have not reached the target ref_pos
#         if tup[0] in [0, 1, 4, 7, 8]:
        #no SC is considered
        if tup[0] in [0, 1, 7, 8]:
            #the start pos of the next cigar tup
            cur_contig_pos += tup[1]
        #if consume ref, have not reached the target ref_pos
        if tup[0] in [0, 2, 3, 7, 8]:
            cur_ref_pos += tup[1]
    #bad return
    #test
    #print("here5")
    return -1
            
#TODO: check +1/-1 position
def modify_cigar(contig, start_pos, end_pos, left):
    
    #left = True if trimming from left
    #modi_contig = copy.deepcopy(contig)
    #if read is covered by another read
    cigar_tuples = contig.cigartuples
    
    if_hc_first = False
    if_hc_last = False
    hc_first_tuple = []
    hc_last_tuple = []
    
    if cigar_tuples[0][0] == 5:
        if_hc_first = True
        hc_first_tuple.append(cigar_tuples[0])
        cigar_tuples = cigar_tuples[1:]
    if cigar_tuples[-1][0] == 5:
        if_hc_last = True
        hc_last_tuple.append(cigar_tuples[-1])
        cigar_tuples = cigar_tuples[0:len(cigar_tuples)-1]
    
    #test
#     print(cigar_tuples)
    
    new_cigars = []
    if end_pos == -1:
        if if_hc_first:
            new_cigars.append(hc_first_tuple[0])
        new_cigars.append((4, contig.infer_query_length()))
        if if_hc_last:
            new_cigars.append(hc_last_tuple[0])
        contig.cigar = new_cigars
    #start_pos, end_pos: trimming start and end on the ref
    #trim from left
    elif left:
        #the no. of bases to be trimmed AFTER soft clip
        trim_base = 0
        #trim start and pos on contig, 0 base
        trim_start_pos = 0
        trim_end_pos = find_query_pos(contig, end_pos)
        
        if trim_end_pos == contig.infer_query_length():
            trim_end_pos -= 1
        
        trim_base = trim_end_pos - trim_start_pos + 1
        
        #test
        #print("here1", trim_base, trim_end_pos)
        #passed_base
        passed_base = 0
        if if_hc_first:
            new_cigars.append(hc_first_tuple[0])
        new_cigars.append((4, trim_base))
        #the first index of cigar tuple that will be kept
        trim_index = 0
        for tup_index, tup in enumerate(cigar_tuples):
            #if consume contig, have reached the target ref_pos
            if tup[0] in [0, 1, 4, 7, 8] and passed_base < trim_base and passed_base + tup[1] >= trim_base:
                if passed_base + tup[1] > trim_base:
                    #test
                    #print("here2", (tup[0], tup[1] - (trim_base - passed_base)))
                    new_cigars.append((tup[0], passed_base + tup[1] - trim_base))
                    #new_cigars.append((tup[0], trim_base - passed_base))
                    trim_index = tup_index + 1
                else:
                    trim_index = tup_index + 1
                break
            #if consume contig
            if tup[0] in [0, 1, 4, 7, 8]:
                passed_base += tup[1]
        
        if trim_index <= len(cigar_tuples) - 1:
            new_cigars.extend(cigar_tuples[trim_index:])
        if if_hc_last:
            new_cigars.append(hc_last_tuple[0])        
        contig.cigar = new_cigars
        #test
        #print("here3", new_cigars)
        contig.reference_start = end_pos + 1
    #trim from right
    elif not left:
        trim_base = 0
        #print("here0", start_pos, end_pos)
        trim_start_pos = find_query_pos(contig, start_pos)
        trim_end_pos = contig.infer_query_length() - 1
        
        if trim_start_pos == contig.infer_query_length():
            trim_start_pos -= 1
        
        trim_base = trim_end_pos - trim_start_pos + 1
        #test
        #print("here1", trim_base, trim_end_pos, trim_start_pos)
        #passed_base
        passed_base = 0
        if if_hc_last:
            new_cigars.append(hc_last_tuple[0])          
        new_cigars = [(4, trim_base)] + new_cigars
        trim_index = 0
        for i in range(len(cigar_tuples)-1, -1, -1):
            tup = cigar_tuples[i]
            #if consume contig, have reached the target ref_pos
            if tup[0] in [0, 1, 4, 7, 8] and passed_base < trim_base and passed_base + tup[1] >= trim_base:
                if passed_base + tup[1] > trim_base:
                    #test
                    #print("here2", (tup[0], tup[1] - (trim_base - passed_base)))
                    new_cigars = [(tup[0], tup[1] - (trim_base - passed_base))] + new_cigars
                    trim_index = i - 1
                else:
                    trim_index = i - 1 
                break
            #if consume contig
            if tup[0] in [0, 1, 4, 7, 8]:
                passed_base += tup[1]
        
        if trim_index != -1:
            new_cigars = cigar_tuples[:trim_index+1] + new_cigars
        if if_hc_first:
            new_cigars = hc_first_tuple + new_cigars      
        contig.cigar = new_cigars
        
        #test
        #print("here3", new_cigars)
    #return modi_contig     
    
            
            
def trim_by_ol(contig, index, contig_list, remove_list):
    #loop through contig_list looking for overlapping
    for i in range(index+1, len(contig_list)):
        contig_start = contig.reference_start
        contig_end = contig.reference_end - 1
        cur_start = contig_list[i].reference_start
        cur_end = contig_list[i].reference_end - 1
            
        #if the short contig is covered by current long contig
        if contig_start >= cur_start and contig_end <= cur_end:
            modify_cigar(contig, 0, -1, False)
            remove_list[index] = 1
            break
        #if overlapping
        elif contig_start <= cur_end and contig_end > cur_end:
                
            modify_cigar(contig, contig_start, cur_end, True)
            
            
        elif contig_start < cur_start and contig_end >= cur_start:
            
            modify_cigar(contig, cur_start, contig_end, False)
    #may not needed
    contig_list[index] = contig     


chr_list = ["1", "2", "3", "4", "5",
            "6", "7", "8", "9", "10",
            "11", "12", "13", "14", "15",
            "16", "17", "18", "19", "20",
            "21", "22", "X", "Y"]
#chr_list = ["2"]

for chr_index in chr_list:
    if chr_index not in infile.references:
        chr_index = 'chr' + chr_index
    if chr_index not in infile.references:
        continue
    if_first = True
    #sort fetched contigs by asending length (.query_alignment_length)
    contig_list = []
    #test
    #for rec in infile.fetch(chr_index, 197556789, 198056789):
    #for rec in infile.fetch(chr_index, 598250, 740208):
    #for rec in infile.fetch(chr_index, 240063977, 240298717):
    for rec in infile.fetch(chr_index):
        #print(rec.reference_start)
        contig_list.append(rec)
    #sort contig_list by length
    mergesort_contigs(contig_list)
    
    remove_list = [0] * len(contig_list)   
    
    
    for index, contig in enumerate(contig_list):
        cigar = contig.cigartuples
        consume_query = [0,1,7,8]
        consumed_base = 0
        for tup in cigar:
            if tup[0] in consume_query:
                consumed_base += tup[1]
        #print("nooooooooo", consumed_base, contig.query_alignment_end - contig.query_alignment_start)
        #print(contig.reference_start, contig.reference_end)
        #print(cigar)
    
    #loop through sorted contig list, trim the shorter contig if overlapping
    for index, contig in enumerate(contig_list):
        trim_by_ol(contig, index, contig_list, remove_list)
    
    #test
    print(chr_index, len(contig_list))
    #print(remove_list)
    for index, contig in enumerate(contig_list):
        if remove_list[index] != 1:
            outfile.write(contig)
            #test
            cigar = contig.cigartuples
            consume_query = [0,1,7,8]
            consumed_base = 0
            for tup in cigar:
                if tup[0] in consume_query:
                    consumed_base += tup[1]
            if consumed_base != contig.query_alignment_end - contig.query_alignment_start:
                print("nooooooooo", consumed_base, contig.query_alignment_end - contig.query_alignment_start)
            #print(contig.reference_start, contig.reference_end)
            #print(cigar)
    #for i in range(0, 100):
    #    print(contig_list[i].query_alignment_length)

infile.close()
outfile.close()
