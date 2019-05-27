package fi.robosailboat.webservice.robosailboatLib.repository;

import fi.robosailboat.webservice.boatCommunication.dto.SensorData;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.time.LocalDateTime;
import java.util.List;

public interface LoggingRepository extends MongoRepository<SensorData,String> {

    SensorData findTopByOrderByCreatedDesc();

    List<SensorData> findByCreatedBetween(LocalDateTime startDate, LocalDateTime endDate);
}
