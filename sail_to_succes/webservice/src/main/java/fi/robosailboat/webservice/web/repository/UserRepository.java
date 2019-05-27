package fi.robosailboat.webservice.web.repository;

import fi.robosailboat.webservice.web.dto.User;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface UserRepository extends MongoRepository<User,String> {
    User findByUserName(String username);
}
