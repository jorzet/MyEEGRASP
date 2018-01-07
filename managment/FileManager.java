/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package managment;

import entities.User;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.JSONException;
import org.json.JSONObject;

/**
 *
 * @author Jorge Zepeda Tinoco
 */
public class FileManager {
    
    public static final String ID_USER = "id_user";
    public static final String DIRECTORY_NAME = "directory_name";
    public static final String DATE_RECORDING = "date_recording";
    public static final String LAST_UPLOADED = "last_uploaded";
    public static final String TOTAL_BYTES = "total_bytes";
    public static final String BYTES_FILE = "bytes_file";
    public static final String CURRENT_POSITION_FILE = "current_position_file";
    
    String path;
    String pathUser;
    String pathFileRecording;
    String subPath;
    File mFile;
            
    public FileManager(String fileName){
        path = "/home/pi" + File.separator + "Documents" + File.separator + "RaspberryRecordings";
        /*File directoryRecordings = new File(path);
        if (! directoryRecordings.exists()){
            directoryRecordings.mkdir();
            System.out.println("crea directorio");
        }*/
        
        pathUser = path + File.separator + "REC";
	subPath = fileName;
	mFile = new File(pathUser + File.separator + fileName);
        System.out.println(pathUser);
        System.out.println(getLatestFilefromDir());
    }
    
    /*public FileManager(String fileName){
        path = System.getProperty("user.home") + File.separator + "Documents" + File.separator + "RaspberryRecordings";
        File directoryRecordings = new File(path);
        if (! directoryRecordings.exists()){
            directoryRecordings.mkdir();
            System.out.println("crea directorio");
        }

        pathUser = path + File.separator + "Data.txt";
        File directoryUser = new File(pathUser);
        if (! directoryUser.exists()){
            directoryUser.mkdir();
            System.out.println("crea directorio usuario");
        }
        
        pathFileRecording = path + File.separator + fileName;
    }*/

    public int getFileSize(){
	return (int)mFile.length();
    }
    
    public User readUserDataFile(){
        try {
            String text = new String(Files.readAllBytes(Paths.get(pathUser)), StandardCharsets.UTF_8);
            JSONObject obj = new JSONObject(text);
            return new User(obj.getInt(ID_USER), obj.getString(DIRECTORY_NAME), obj.getString(DATE_RECORDING), obj.getBoolean(LAST_UPLOADED));
        } catch (JSONException | IOException ex) {
            Logger.getLogger(FileManager.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
    
    public void writeUserDataFile(int idUser, String userName, String dateRecording, boolean isLastRecordingUploaded){
        JSONObject jsonData = new JSONObject();
        try {
            jsonData.put(ID_USER, idUser);
            jsonData.put(DIRECTORY_NAME, userName);
            jsonData.put(DATE_RECORDING, dateRecording);
            jsonData.put(LAST_UPLOADED, isLastRecordingUploaded);
            
        } catch (JSONException ex) {
            System.err.print(ex);
        }
    }
    
    public byte[] readFile(int position){
        RandomAccessFile inputStream;
	int tam = getFileSize()-position; 
	byte[] data;

	if (tam < 100) 
	   data = new byte[tam];
	else
	   data = new byte[100];
        
        try {
            inputStream = new RandomAccessFile(pathUser + File.separator + subPath,"rw");
            inputStream.seek(position);
            if((inputStream.read(data)) != -1){
                return data;
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(FileManager.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(FileManager.class.getName()).log(Level.SEVERE, null, ex);
        }       
        return null;
    }
    
    public int writeFile(){
        
        return 0;
    }
    
    private File getLatestFilefromDir(){
        File dir = new File(path);
System.out.println("path: " + path);
        File[] files = dir.listFiles();
        if (files == null || files.length == 0) {
            System.out.println("entra if");
            return null;
        }
System.out.println("no entra if ");

        File lastModifiedFile = files[0];
        for (int i = 1; i < files.length; i++) {
           if (lastModifiedFile.lastModified() < files[i].lastModified()) {
               lastModifiedFile = files[i];
           }
        }
        return lastModifiedFile;
    }

    public void removeAllFiles(){
       for (File file: new File(pathUser).listFiles())
		if(!file.isDirectory())
			file.delete();
    }
}
