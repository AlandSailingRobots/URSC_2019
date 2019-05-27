package fi.robosailboat.webservice.boatCommunication.dto;

import lombok.Data;

import static java.lang.String.format;

@Data
public class PostResponse {

    private String c; // command with rudder angle + sail angle + desired heading

    public PostResponse(final String r, final String s, final String d){
        this.c = r + s + d;
    }
}
