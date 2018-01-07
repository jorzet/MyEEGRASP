/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package connection;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;


/**
 *
 * @author Jorge Zepeda Tinoco
 */
public class HttpRequest {
    private static final String BASE_URL_PATH = "/usr/local/lib/python3.4/dist-packages/configNetwork.txt";
    private static final String GET_STORE_RECORDING = "/storefilerecording/";
    private static final int CONNECT_TIMEOUT = 50000; // 50 seconds
    private static final int READ_TIMEOUT = 55000; // 15 seconds

    public static boolean isConnected() {
        //TODO
        return true;
    }

    public static String sendGetRequest(String json)  {
	File configNetworkFile = new File(BASE_URL_PATH);
	BufferedReader br;
	String BASE_URL = "";
	try {
		br = new BufferedReader(new FileReader(configNetworkFile));
		BASE_URL = br.readLine();
	} catch(Exception e){
		e.printStackTrace();
	}

        String url = BASE_URL + GET_STORE_RECORDING + json.replace("{", "%7B").replace("}", "%7D");
        URL urlObj = null;
        try {
            urlObj = new URL(url);
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }

        HttpURLConnection urlConnection = null;
        try {
            urlConnection = (HttpURLConnection) urlObj.openConnection();
            urlConnection.setConnectTimeout(CONNECT_TIMEOUT);
            urlConnection.setReadTimeout(READ_TIMEOUT);
            urlConnection.setRequestMethod("GET");
            urlConnection.setRequestProperty("Accept", "application/json");
            urlConnection.setUseCaches(true);

            InputStream is = new BufferedInputStream(urlConnection.getInputStream());

            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(is, "UTF-8"));
            StringBuilder total = new StringBuilder();

            String line;
            while ((line = bufferedReader.readLine()) != null) {
                total.append(line);
            }

            if (urlConnection != null) {
                urlConnection.disconnect();
            }

            return total.toString();
        } catch (IOException e) {
            e.printStackTrace();
            if (urlConnection != null) {
                urlConnection.disconnect();
            }
            return null;
        } finally {
            
            if (urlConnection != null) {
                urlConnection.disconnect();
                System.out.println("Conexxion exitosa");
            }
        }
    }


}
