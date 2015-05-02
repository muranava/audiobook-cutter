filename="./output.txt"

output_tracks=./output_tracks
input_track=./input.mp3
output_text=./result.txt

rm -rf ${output_tracks}
mkdir ${output_tracks}

rm ${output_text}

while read -r line
do
    track=`echo $line | cut -d= -f1 `
    track_padded="$(printf '%03d' $track)"
    start_time=`echo $line | cut -d= -f2`
    length=`echo $line | cut -d= -f3`
    text=`echo $line | cut -d= -f4`


    avconv -ss $start_time -t $length -i ${input_track} -acodec copy ${output_tracks}/${track_padded}.mp3


    
    echo "${text} (${track})" | sed -re 's/\\n/\n/g' >> ${output_text}
    echo >> ${output_text}

done < "$filename"



