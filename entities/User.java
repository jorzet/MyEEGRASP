/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package entities;

/**
 *
 * @author Jorge
 */
public class User {
    private int idUser;
    private String userName;
    private String dateRecording;
    private boolean isLastRecordingUploaded;
    
    public User(int idUser, String userName, String dateRecording, boolean isLastRecordingUploaded){
        this.idUser = idUser;
        this.userName = userName;
        this.dateRecording = dateRecording;
        this.isLastRecordingUploaded = isLastRecordingUploaded;
    }
    
    public int getIdUser(){
        return this.idUser;
    }
    
    public String getUserNamer(){
        return this.userName;
    }
    
    public String getDateRecording(){
        return this.dateRecording;
    }
    
    public boolean GetIsLastRecordingUploaded(){
        return this.isLastRecordingUploaded;
    }
}
