/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

import connection.HttpRequest;
import java.util.logging.Level;
import java.util.logging.Logger;
import managment.FileManager;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONArray;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;


/**
 *
 * @author Jorge Zepeda Tinoco
 */
public class RaspberryClientWS {
    /**
     * @param args the command line arguments
     */

    public static final String ID_USER = "id_user";
    public static final String FILE_NAME = "file_name";
    public static final String DATE_RECORDING = "date_recording";
    public static final String CHANNEL_LIST = "channel_list";
    public static final String SCHEDULE_ID = "schedule_id";
    public static final String LAST_UPLOADED = "last_uploaded";
    public static final String TOTAL_BYTES = "total_bytes";
    public static final String BYTES_FILE = "bytes_file";
    public static final String CURRENT_POSITION_FILE = "current_position_file";

    public static final String TRANSFER_STATUS_RECORDING = "transfer_status_recording";
    public static final String FINAL_POSITION_FILE = "final_position_file";

    public static final int ERROR_FROM_JSON = 0x07;
    public static final int CODE_SUCESSFULL_STORE_RECORDING = 0x14;
    public static final int CODE_SUCESSFULL_TRANSFER_FILES_COMPLETE = 0xA2;

    public static final String INFO_SCHEDULE_PATH = "/home/pi/Documents/RaspberryRecordings/infoSchedule.txt";
    public static final String STATUS_FILE_PATH = "/home/pi/Documents/RaspberryRecordings/statusFile.txt";

    private static FileManager fm;

    public static String[] channels;

    public static void main(String[] args) {
	int status = 0;
	String channelList = "";

	File jsonFile = new File(INFO_SCHEDULE_PATH);
        File statusFile = new File(STATUS_FILE_PATH);
        
	BufferedReader br;
	BufferedWriter bw;
	int idUser=0;
	int idSchedule=0;
	String date="";
	try{
		br = new BufferedReader(new FileReader(jsonFile));
		String readedJson = br.readLine();
                //String readedJson = "{\"id_patient\":14,\"id_schedule\":18,\"duration\":\"00:00:10\",\"date\":\"03\\/15\\/2017\",\"channels\":[{\"channel\":\"FP1\"},{\"channel\":\"FP2\"}],\"mac_address\":[{\"mac\":\"CC:2F:DE:C6:61:D2\"},{\"mac\":\"C5:2C:8A:46:C7:74\"}]}";
		System.out.println(readedJson.substring(1,readedJson.length()-1).replace("\\",""));
		br.close();
		JSONObject jsonChannels = new JSONObject(readedJson.substring(1,readedJson.length()-1).replace("\\",""));
		JSONArray channelsArray = jsonChannels.getJSONArray("channels");
                channels = new String[channelsArray.length()];

		idUser = jsonChannels.getInt("id_patient");
		idSchedule = jsonChannels.getInt("id_schedule");
		date = jsonChannels.getString("date");

		for(int i =0;i<channelsArray.length();i++){
			JSONObject jsonChannel = channelsArray.getJSONObject(i);
			String channelName = jsonChannel.getString("channel");
                        channels[i]=channelName;
		}

	} catch(Exception e){
		e.printStackTrace();
	}

	for(int i =0; i<channels.length; i++)
		channelList = channelList + channels[i] + ",";

	for(int i =0; i<channels.length; i++){
		fm = new FileManager(channels[i]+".bin");
		long totalSize = fm.getFileSize();
	
		int pos = 0;
		boolean isResponse = true;
		String response = "";
		System.out.println("size" +totalSize);
	
		while(pos<totalSize){
	            if(isResponse){
	
		        byte[] file = fm.readFile(pos);
		        JSONObject jsonRecording = new JSONObject();
		        
		        try {
		            jsonRecording.put(ID_USER, idUser+"");
			    jsonRecording.put(DATE_RECORDING, date.replace("/", "-"));
			    jsonRecording.put(CHANNEL_LIST, channelList.substring(0,channelList.length()-1));
		            jsonRecording.put(FILE_NAME, channels[i]);
		            jsonRecording.put(SCHEDULE_ID, idSchedule+"");
		            jsonRecording.put(TOTAL_BYTES, totalSize);
		            jsonRecording.put(CURRENT_POSITION_FILE, pos);
		            jsonRecording.put(BYTES_FILE, file);
		            
		            String json = jsonRecording.toString();
			    isResponse = false;
		            response = HttpRequest.sendGetRequest(json.replace("{", "%7B").replace("}", "%7D"));
		            System.out.println(response);

			    JSONObject jsonStatus = new JSONObject(response);
			    pos = jsonStatus.getInt(FINAL_POSITION_FILE);
                            status = jsonStatus.getInt(TRANSFER_STATUS_RECORDING);
			    
			    System.out.println("pos:"+pos);
			    response = "";
			    
	
		        } catch (JSONException ex) {
		            System.err.print(ex);
		        }
		    }else if(response.equals("")){
			isResponse = true;
		    }
		}

		
	}
	if(status==CODE_SUCESSFULL_TRANSFER_FILES_COMPLETE){
	   System.out.println("elimina archivos");
	   try {
	   	fm.removeAllFiles();
		bw = new BufferedWriter(new FileWriter(statusFile));
		bw.write("0");
		bw.close();
		System.out.println("currect status: 0");
	   } catch(Exception e){
		e.printStackTrace();
	   }
	}
    }
    
}
