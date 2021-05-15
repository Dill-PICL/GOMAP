echo off all
pkg load dataframe;
cd $PATH;
disp("Reading fasta file")
disp('$INPUT_FASTA')
[Headers, Sequences] = fastaread('$INPUT_FASTA');
disp("Starting Predictions")
PRED=MAIN(Sequences);
disp("Finished Predictions")
tbnames = horzcat('gene_id',PRED.accessions);
tbnames = strrep(tbnames,':','_');
disp("Writing the output")
disp('$OUTPUT_SCORE')
fid = fopen('$OUTPUT_SCORE', 'w');
fputs(fid, strjoin(tbnames, "\t"));
fprintf(fid, '\n');
for i = 1:columns(Headers)
  fprintf(fid, '%s', strtok(Headers{i}));
  fprintf(fid, '\t%.4e', PRED.scores(i,:));
  fprintf(fid, '\n');
endfor
fclose(fid);
