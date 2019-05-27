package fi.robosailboat.webservice.web.dto;

import lombok.Data;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Data
@Document("User")
public class User {
    @Id
    public ObjectId _id;
    public String userName;
    public String password;
}
