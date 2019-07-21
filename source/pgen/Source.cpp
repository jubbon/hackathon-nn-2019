#include "Header.h"
#include <string>
#include <fstream>
#include <streambuf>
#include <vector>
#include <map>
#include <random>
#include <iostream>
#include <algorithm>
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/prettywriter.h"

#include "settings.h"

//! Разбиение карты по шестиугольникам
std::vector <hexagon> hexagons;

size_t homeSum = 0;
size_t mollSum = 0;
size_t educationSum = 0;
size_t officeSum = 0;
size_t plantSum = 0;
size_t sportSum = 0;
size_t hospitalSum = 0;
size_t entertaimentSum = 0;
size_t stationsSum = 0;
size_t attractionsSum = 0;

// Функции

//! \brief Конвертация времени в строку
//! \param [in] time - время в минутах, в пределах одних суток
//! \return Время в виде строки в формате hh:mm
std::string TimeToStr(size_t time);

//------------------------------------------------------------------------------------------------
// Распределение людей по категориям в течении заданного промежутка времени
/*1 */ std::map < size_t, size_t > matrDISTR_home          ;
/*2 */ std::map < size_t, size_t > matrDISTR_moll          ;
/*3 */ std::map < size_t, size_t > matrDISTR_education     ;
/*4 */ std::map < size_t, size_t > matrDISTR_office        ;
/*5 */ std::map < size_t, size_t > matrDISTR_plant         ;
/*6 */ std::map < size_t, size_t > matrDISTR_sport         ;
/*7 */ std::map < size_t, size_t > matrDISTR_hospital      ;
/*8 */ std::map < size_t, size_t > matrDISTR_entertaiment  ;
/*9 */ std::map < size_t, size_t > matrDISTR_stations      ;
/*10*/ std::map < size_t, size_t > matrDISTR_attractions   ;

//------------------------------------------------------------------------------------------------
//! Получение случайного числа в заданном промежутке
size_t getRandValue(size_t a, size_t b);

//------------------------------------------------------------------------------------------------
//! Распределение людей по категориям с учетом их приоритета на заданное время
void peopleToHome(std::vector <hexagon> &state, size_t time);

//------------------------------------------------------------------------------------------------
//! На основе сгенерированных случайных распределений определение переходом между ячейками
void detectRouting(std::map < size_t, std::vector <hexagon> > &peopleFinishState);

//------------------------------------------------------------------------------------------------
int main(int argc, char *argv[])
{
    // Инициализация настроек по умолчанию
    auto &settings = Settings::Instance();

    // Чтение настроек
    settings.readSetting();

    std::cout << "Simulation Start.\n";

    // 0 шаг. Преинициализация состояния
    
    std::cout << "Start reading map...\n";

    std::string filename;
    if (argc > 1)
    {
        filename = argv[1];
    }
    else
    {
        std::cout << "Set file name in argument" << "\n";
        return 1;
    }

    std::ifstream map(filename.c_str());

    std::string str((std::istreambuf_iterator<char>(map)), {});
    std::cout << "Reading map Done.\n";
    if (str.empty())
    {
        std::cout << "File map.json is empty..." << "\n";
        return 1;
    }
    map.close();

    std::cout << "Start parsing map...\n";
    rapidjson::Document document;
    document.Parse(str.c_str());

    if (document.HasParseError())
    {
        std::cout << "Document parser error: " << document.GetParseError() << "\n";
        std::cout << "Error code:\n" << "0. No error.\n\
        1. The document is empty.\n\
        2. The document root must not follow by other values.\n\
        3. Invalid value.\n\
        4. Missing a name for object member.\n\
        5. Missing a colon after a name of object member.\n\
        6. Missing a comma or '}' after an object member.\n\
        7. Missing a comma or ']' after an array element.\n\
        8. Incorrect hex digit after \\u escape in string.\n\
        9. The surrogate pair in string is invalid.\n\
        10. Invalid escape character in string.\n\
        11. Missing a closing quotation mark in string.\n\
        12. Invalid encoding in string.\n\
        13. Number too big to be stored in double.\n\
        14. Miss fraction part in number.\n\
        15. Miss exponent in number.\n\
        16. Parsing was terminated.\n\
        17. Unspecific syntax error.\n";
        return 1;
    }

    for (auto itr = document.MemberBegin(); itr != document.MemberEnd(); ++itr)
    {
        hexagon hex;
        
        hex.index = itr->name.GetString();
        if (auto elem = itr->value.IsObject())
        {
            auto &value = itr->value;
            if (value.HasMember ("population"))
                hex.population = value["population"].GetUint();

            if (value.HasMember("infrastructure"))
            {
                if (value["infrastructure"].IsObject())
                {
                    auto &infra = value["infrastructure"];

                    if (infra.HasMember("home"))
                        hex.infra.home = static_cast <size_t> (round( infra["home"].GetDouble() * 10));

                    if (infra.HasMember("mall"))
                        hex.infra.moll = static_cast <size_t> (round(infra["mall"].GetDouble() * 10));

                    if (infra.HasMember("education"))
                        hex.infra.education = static_cast <size_t> (round(infra["education"].GetDouble() * 10));

                    if (infra.HasMember("commercial"))
                        hex.infra.office = static_cast <size_t> (round(infra["commercial"].GetDouble() * 10));

                    if (infra.HasMember("industrial"))
                        hex.infra.plant = static_cast <size_t> (round(infra["industrial"].GetDouble() * 10));

                    if (infra.HasMember("sport"))
                        hex.infra.sport = static_cast <size_t> (round(infra["sport"].GetDouble() * 10));

                    if (infra.HasMember("health"))
                        hex.infra.hospital = static_cast <size_t> (round(infra["health"].GetDouble() * 10));

                    if (infra.HasMember("entertaiment"))
                        hex.infra.entertaiment = static_cast <size_t> (round(infra["entertaiment"].GetDouble() * 10));

                    if (infra.HasMember("stations"))
                        hex.infra.stations = static_cast <size_t> (round(infra["stations"].GetDouble() * 10));

                    if (infra.HasMember("attractions"))
                        hex.infra.attractions = static_cast <size_t> (round(infra["attractions"].GetDouble() * 10));
                }
            }
        }
        hexagons.emplace_back(hex);
    }

    std::cout << "Parsing map Done.\n";

    // Подсчет общего количества жителей
    size_t allPeopleCount = 0;
    for (auto &i : hexagons)
        allPeopleCount += i.population;

    auto PeopleCount = allPeopleCount;
    allPeopleCount = static_cast<size_t> (floor(static_cast< double > (allPeopleCount) * settings.publicTransportUsePercent));

    for (auto &i : hexagons)
    {
        homeSum += i.infra.home;
        mollSum += i.infra.moll;
        educationSum += i.infra.education;
        officeSum += i.infra.office;
        plantSum += i.infra.plant;
        sportSum += i.infra.sport;
        hospitalSum += i.infra.hospital;
        entertaimentSum += i.infra.entertaiment;
        stationsSum += i.infra.stations;
        attractionsSum += i.infra.attractions;
    }

    // Инициализация Стохастических данных в определенные моменты времени по параболе
    paramParab _pABC_education    ( timePick ( 50  , 75  , 10  , 7   , 14  , 17   ) ) ;
    paramParab _pABC_plant        ( timePick ( 75  , 98  , 3   , 7   , 15  , 20   ) ) ;
    paramParab _pABC_moll         ( timePick ( 10  , 100 , 50  , 8   , 14  , 21   ) ) ;
    paramParab _pABC_office       ( timePick ( 80  , 100 , 5   , 9   , 15  , 19   ) ) ;
    paramParab _pABC_sport        ( timePick ( 30  , 70  , 2   , 5   , 15  , 20   ) ) ;
    paramParab _pABC_hospital     ( timePick ( 40  , 100 , 20  , 5   , 9   , 23   ) ) ;
    paramParab _pABC_stations     ( timePick ( 20  , 88  , 31  , 6   , 14  , 23   ) ) ;
    paramParab _pABC_entertaiment ( timePick ( 5   , 40  , 50  , 9   , 13  , 23   ) ) ;
    paramParab _pABC_attractions  ( timePick ( 20  , 77  , 50  , 10  , 16  , 23   ) ) ;
    paramParab _pABC_home         ( timePick ( 95  , 10  , 95  , 5   , 12  , 23   ) ) ;

    auto simulationTime = settings.start_time;

    std::map < size_t, double > matrA_education    ;
    std::map < size_t, double > matrA_plant        ;
    std::map < size_t, double > matrA_moll         ;
    std::map < size_t, double > matrA_office       ;
    std::map < size_t, double > matrA_sport        ;
    std::map < size_t, double > matrA_hospital     ;
    std::map < size_t, double > matrA_stations     ;
    std::map < size_t, double > matrA_entertaiment ;
    std::map < size_t, double > matrA_attractions  ;
    std::map < size_t, double > matrA_home         ;
    
    while (simulationTime <= settings.finish_time)
    {
        matrA_education    [ simulationTime ] = _pABC_education    .a * simulationTime * simulationTime + _pABC_education    .b * simulationTime + _pABC_education    .c;
        matrA_plant        [ simulationTime ] = _pABC_plant        .a * simulationTime * simulationTime + _pABC_plant        .b * simulationTime + _pABC_plant        .c;
        matrA_moll         [ simulationTime ] = _pABC_moll         .a * simulationTime * simulationTime + _pABC_moll         .b * simulationTime + _pABC_moll         .c;
        matrA_office       [ simulationTime ] = _pABC_office       .a * simulationTime * simulationTime + _pABC_office       .b * simulationTime + _pABC_office       .c;
        matrA_sport        [ simulationTime ] = _pABC_sport        .a * simulationTime * simulationTime + _pABC_sport        .b * simulationTime + _pABC_sport        .c;
        matrA_hospital     [ simulationTime ] = _pABC_hospital     .a * simulationTime * simulationTime + _pABC_hospital     .b * simulationTime + _pABC_hospital     .c;
        matrA_stations     [ simulationTime ] = _pABC_stations     .a * simulationTime * simulationTime + _pABC_stations     .b * simulationTime + _pABC_stations     .c;
        matrA_entertaiment [ simulationTime ] = _pABC_entertaiment .a * simulationTime * simulationTime + _pABC_entertaiment .b * simulationTime + _pABC_entertaiment .c;
        matrA_attractions  [ simulationTime ] = _pABC_attractions  .a * simulationTime * simulationTime + _pABC_attractions  .b * simulationTime + _pABC_attractions  .c;
        matrA_home         [ simulationTime ] = _pABC_home         .a * simulationTime * simulationTime + _pABC_home         .b * simulationTime + _pABC_home         .c;

        if ( matrA_education    [ simulationTime ] < 0 ) matrA_education    [ simulationTime ] = 0 ;
        if ( matrA_plant        [ simulationTime ] < 0 ) matrA_plant        [ simulationTime ] = 0 ;
        if ( matrA_moll         [ simulationTime ] < 0 ) matrA_moll         [ simulationTime ] = 0 ;
        if ( matrA_office       [ simulationTime ] < 0 ) matrA_office       [ simulationTime ] = 0 ;
        if ( matrA_sport        [ simulationTime ] < 0 ) matrA_sport        [ simulationTime ] = 0 ;
        if ( matrA_hospital     [ simulationTime ] < 0 ) matrA_hospital     [ simulationTime ] = 0 ;
        if ( matrA_stations     [ simulationTime ] < 0 ) matrA_stations     [ simulationTime ] = 0 ;
        if ( matrA_entertaiment [ simulationTime ] < 0 ) matrA_entertaiment [ simulationTime ] = 0 ;
        if ( matrA_attractions  [ simulationTime ] < 0 ) matrA_attractions  [ simulationTime ] = 0 ;
        if ( matrA_home         [ simulationTime ] < 0 ) matrA_home         [ simulationTime ] = 0 ;

        simulationTime += settings.interval;
    }

    std::map < size_t, double > matrRAND_education   ;
    std::map < size_t, double > matrRAND_plant       ;
    std::map < size_t, double > matrRAND_moll        ;
    std::map < size_t, double > matrRAND_office      ;
    std::map < size_t, double > matrRAND_sport       ;
    std::map < size_t, double > matrRAND_hospital    ;
    std::map < size_t, double > matrRAND_stations    ;
    std::map < size_t, double > matrRAND_entertaiment;
    std::map < size_t, double > matrRAND_attractions ;
    std::map < size_t, double > matrRAND_home        ;

    simulationTime = settings.start_time;

    matrRAND_education   [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_education    [ simulationTime ] ))));
    matrRAND_plant       [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_plant        [ simulationTime ] ))));
    matrRAND_moll        [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_moll         [ simulationTime ] ))));
    matrRAND_office      [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_office       [ simulationTime ] ))));
    matrRAND_sport       [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_sport        [ simulationTime ] ))));
    matrRAND_hospital    [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_hospital     [ simulationTime ] ))));
    matrRAND_stations    [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_stations     [ simulationTime ] ))));
    matrRAND_entertaiment[ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_entertaiment [ simulationTime ] ))));
    matrRAND_attractions [ simulationTime ] = static_cast < double > (getRandValue ( 0  , static_cast < size_t > ( floor (matrA_attractions  [ simulationTime ] ))));
    matrRAND_home        [ simulationTime ] = static_cast < double > (std::min ( 40, static_cast < int > ( floor ( matrA_home          [ simulationTime ] )) ), 
                                                                      std::max ( 40, static_cast < int > ( floor ( matrA_home          [simulationTime]   )) ));

    simulationTime += settings.interval;

    while (simulationTime <= settings.finish_time)
    {
        matrRAND_education   [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_education    [ simulationTime - settings.interval ] , matrA_education    [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_education    [ simulationTime - settings.interval ] , matrA_education    [ simulationTime ] ) ))));
        matrRAND_plant       [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_plant        [ simulationTime - settings.interval ] , matrA_plant        [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_plant        [ simulationTime - settings.interval ] , matrA_plant        [ simulationTime ] ) ))));
        matrRAND_moll        [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_moll         [ simulationTime - settings.interval ] , matrA_moll         [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_moll         [ simulationTime - settings.interval ] , matrA_moll         [ simulationTime ] ) ))));
        matrRAND_office      [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_office       [ simulationTime - settings.interval ] , matrA_office       [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_office       [ simulationTime - settings.interval ] , matrA_office       [ simulationTime ] ) ))));
        matrRAND_sport       [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_sport        [ simulationTime - settings.interval ] , matrA_sport        [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_sport        [ simulationTime - settings.interval ] , matrA_sport        [ simulationTime ] ) ))));
        matrRAND_hospital    [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_hospital     [ simulationTime - settings.interval ] , matrA_hospital     [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_hospital     [ simulationTime - settings.interval ] , matrA_hospital     [ simulationTime ] ) ))));
        matrRAND_stations    [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_stations     [ simulationTime - settings.interval ] , matrA_stations     [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_stations     [ simulationTime - settings.interval ] , matrA_stations     [ simulationTime ] ) ))));
        matrRAND_entertaiment[ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_entertaiment [ simulationTime - settings.interval ] , matrA_entertaiment [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_entertaiment [ simulationTime - settings.interval ] , matrA_entertaiment [ simulationTime ] ) ))));
        matrRAND_attractions [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_attractions  [ simulationTime - settings.interval ] , matrA_attractions  [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_attractions  [ simulationTime - settings.interval ] , matrA_attractions  [ simulationTime ] ) ))));
        matrRAND_home        [ simulationTime ] = static_cast < double > (getRandValue ( static_cast < size_t > ( floor ( std::min ( matrA_home         [ simulationTime - settings.interval ] , matrA_home         [ simulationTime ] ) )), static_cast < size_t > ( floor ( std::max ( matrA_home         [ simulationTime - settings.interval ] , matrA_home         [ simulationTime ] ) ))));

        simulationTime += settings.interval;
    }

    simulationTime = settings.start_time;
    while ( simulationTime <= settings.finish_time )
    {
        auto sum =
            matrRAND_education   [ simulationTime ] +
            matrRAND_plant       [ simulationTime ] +
            matrRAND_moll        [ simulationTime ] +
            matrRAND_office      [ simulationTime ] +
            matrRAND_sport       [ simulationTime ] +
            matrRAND_hospital    [ simulationTime ] +
            matrRAND_stations    [ simulationTime ] +
            matrRAND_entertaiment[ simulationTime ] +
            matrRAND_attractions [ simulationTime ] +
            matrRAND_home        [ simulationTime ] ;

        matrDISTR_education     [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_education   [ simulationTime ] / sum ));
        matrDISTR_plant         [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_plant       [ simulationTime ] / sum ));
        matrDISTR_moll          [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_moll        [ simulationTime ] / sum ));
        matrDISTR_office        [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_office      [ simulationTime ] / sum ));
        matrDISTR_sport         [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_sport       [ simulationTime ] / sum ));
        matrDISTR_hospital      [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_hospital    [ simulationTime ] / sum ));
        matrDISTR_stations      [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_stations    [ simulationTime ] / sum ));
        matrDISTR_entertaiment  [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_entertaiment[ simulationTime ] / sum ));
        matrDISTR_attractions   [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_attractions [ simulationTime ] / sum ));
        matrDISTR_home          [ simulationTime ] = static_cast < size_t > ( round ( static_cast < double > ( allPeopleCount ) * matrRAND_home        [ simulationTime ] / sum ));

        simulationTime += settings.interval;
    }

    /////////////////////////////////////////////////////////////////////////
    simulationTime = settings.start_time;
    std::ofstream peopleDistr("peopledistribution.csv");

    peopleDistr << "----" << settings.delimery;
    for (auto it = matrDISTR_moll.begin(); it != matrDISTR_moll.end(); ++it)
    {
        std::string outTime = (settings.timeStr) ? TimeToStr(it->first) : std::to_string(it->first);
        peopleDistr << outTime << settings.delimery;
    }
    peopleDistr << "\n";

    peopleDistr << "education" << settings.delimery;
    for (auto it = matrDISTR_education   .begin(); it != matrDISTR_education   .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "plant" << settings.delimery; 
    for (auto it = matrDISTR_plant       .begin(); it != matrDISTR_plant       .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "moll" << settings.delimery;
    for (auto it = matrDISTR_moll        .begin(); it != matrDISTR_moll        .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "office" << settings.delimery; 
    for (auto it = matrDISTR_office      .begin(); it != matrDISTR_office      .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "sport" << settings.delimery;
    for (auto it = matrDISTR_sport       .begin(); it != matrDISTR_sport       .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "hospital" << settings.delimery; 
    for (auto it = matrDISTR_hospital    .begin(); it != matrDISTR_hospital    .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "stations" << settings.delimery; 
    for (auto it = matrDISTR_stations    .begin(); it != matrDISTR_stations    .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "entertaiment" << settings.delimery; 
    for (auto it = matrDISTR_entertaiment.begin(); it != matrDISTR_entertaiment.end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "attractions" << settings.delimery; 
    for (auto it = matrDISTR_attractions .begin(); it != matrDISTR_attractions .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";
    peopleDistr << "home" << settings.delimery; 
    for (auto it = matrDISTR_home        .begin(); it != matrDISTR_home        .end(); ++it)        peopleDistr << it->second << settings.delimery;    peopleDistr << "\n";

    peopleDistr << "\nAll people count in country: " << PeopleCount;
    peopleDistr.flush();
    peopleDistr.close();
    /////////////////////////////////////////////////////////////////////////

    // 1 step. Init state
    std::map <size_t, std::vector <hexagon>> peopleMoving;
    peopleMoving.insert({ settings.start_time, hexagons });

    peopleToHome(peopleMoving[settings.start_time], settings.start_time);

    // 2 step
    simulationTime = settings.start_time;
    while (simulationTime < settings.finish_time)
    {
        simulationTime += settings.interval;
        auto simulateHexs = (--peopleMoving.end())->second;
        peopleToHome(simulateHexs, simulationTime);
        peopleMoving.insert({ simulationTime, simulateHexs });
    }

    // Последний шаг. Определение путей перемещения
    detectRouting(peopleMoving);

    // Подсчет количества жителей
    size_t curTime = settings.start_time;
    std::ofstream peopleCount("task2.csv");
    while (curTime <= settings.finish_time)
    {
        std::string outTime = (settings.timeStr) ? TimeToStr(curTime) : std::to_string(curTime);

        auto it = peopleMoving.find(curTime);
        if ( it != peopleMoving.end())
        {
            auto peoplestate = it->second;
            size_t peopleCountForTime = 0;
            for (auto &hex : peoplestate)
            {
                peopleCount << outTime << settings.delimery << hex.index << settings.delimery << hex.population << '\n';
                peopleCountForTime += hex.population;
            }
            #ifdef DEBUG
                //peopleCount << "All People count: " << peopleCountForTime << " for time: " << outTime << "\n\n";
            #endif // DEBUG
        }

        curTime += settings.interval;
        peopleCount.flush();
    }
    peopleCount.close();

    std::cout << "Simulation Done.\n";
    return 0;
}

std::string TimeToStr(size_t time)
{
    size_t hh = time / 60;
    size_t mm = time - hh * 60;

    std::string t;

    if (hh < 10)
        t.append("0");
    t.append(std::to_string(hh));
    t.append(":");

    if (mm < 10)
        t.append("0");
    t.append(std::to_string(mm));

    return t;
}

void peopleToHome(std::vector< hexagon> &state, size_t time)
{
    std::string outTime = (Settings::Instance().timeStr) ? TimeToStr(time) : std::to_string(time);
    std::cout << "People distribution for time: " << outTime << "\n";

    auto counthome          = matrDISTR_home        [time];
    auto countmoll          = matrDISTR_moll        [time];
    auto counteducation     = matrDISTR_education   [time];
    auto countoffice        = matrDISTR_office      [time];
    auto countplant         = matrDISTR_plant       [time];
    auto countsport         = matrDISTR_sport       [time];
    auto counthospital      = matrDISTR_hospital    [time];
    auto countentertaiment  = matrDISTR_entertaiment[time];
    auto countstations      = matrDISTR_stations    [time];
    auto countattractions   = matrDISTR_attractions [time];

    for (size_t index = 0; index < state.size(); ++index)
    {
        state [ index ].infra.home         = homeSum         != 0 ? counthome         * hexagons[index].infra.home         / homeSum         : 0;
        state [ index ].infra.moll         = mollSum         != 0 ? countmoll         * hexagons[index].infra.moll         / mollSum         : 0;
        state [ index ].infra.education    = educationSum    != 0 ? counteducation    * hexagons[index].infra.education    / educationSum    : 0;
        state [ index ].infra.office       = officeSum       != 0 ? countoffice       * hexagons[index].infra.office       / officeSum       : 0;
        state [ index ].infra.plant        = plantSum        != 0 ? countplant        * hexagons[index].infra.plant        / plantSum        : 0;
        state [ index ].infra.sport        = sportSum        != 0 ? countsport        * hexagons[index].infra.sport        / sportSum        : 0;
        state [ index ].infra.hospital     = hospitalSum     != 0 ? counthospital     * hexagons[index].infra.hospital     / hospitalSum     : 0;
        state [ index ].infra.entertaiment = entertaimentSum != 0 ? countentertaiment * hexagons[index].infra.entertaiment / entertaimentSum : 0;
        state [ index ].infra.stations     = stationsSum     != 0 ? countstations     * hexagons[index].infra.stations     / stationsSum     : 0;
        state [ index ].infra.attractions  = attractionsSum  != 0 ? countattractions  * hexagons[index].infra.attractions  / attractionsSum  : 0;

        state[index].population = 
            state [ index ].infra.home + 
            state [ index ].infra.moll + 
            state [ index ].infra.education + 
            state [ index ].infra.office + 
            state [ index ].infra.plant + 
            state [ index ].infra.sport +
            state [ index ].infra.hospital + 
            state [ index ].infra.entertaiment + 
            state [ index ].infra.stations + 
            state [ index ].infra.attractions  ;
    }
}

void detectRouting(std::map < size_t, std::vector <hexagon> > &peopleFinishState)
{
    std::cout << "Start People routing\n";

    std::ofstream peopleRouting("task1.csv");
    auto iter = peopleFinishState.begin();
    auto preview = iter;
    ++iter;

    for (; iter != peopleFinishState.end(); ++iter)
    {
        std::string outTime = (Settings::Instance().timeStr) ? TimeToStr(iter->first) : std::to_string(iter->first);
        std::cout << "Preparing time: " << outTime << "\n";

        std::vector< std::pair < int, std::string > > hexDelta;
        auto previewVec = preview->second;
        auto currentVec = iter->second;
        
        auto count = currentVec.size();
        for (size_t i = 0; i < count; ++i)
        {
            int delta = static_cast <int> (currentVec[i].population) - static_cast <int> (previewVec[i].population);
            hexDelta.emplace_back(std::make_pair(delta, currentVec[i].index));
        }

        std::sort(hexDelta.begin(), hexDelta.end(), [](const auto &lhs, const auto &rhs)
        {
            return lhs.first < rhs.first;
        });

        bool findRoute = false;
        size_t startPoint = 0;

        while (!findRoute)
        {
            bool isExistMinus = false;
            for (size_t i = startPoint; i < hexDelta.size(); ++i)
            {
                if (hexDelta[i].first < 0)
                {
                    isExistMinus = true;
                    break;
                }
            }
            if (!isExistMinus)
            {
                findRoute = true;
                break;
            }

            size_t i = 0;
            for ( i = startPoint + 1; i < hexDelta.size(); ++i)
            {
                if (hexDelta[i].first > 0)
                {
                    if (abs(hexDelta[startPoint].first) > abs(hexDelta[i].first))
                    {
                        peopleRouting << outTime << Settings::Instance().delimery << hexDelta[startPoint].second << Settings::Instance().delimery <<
                            hexDelta[i].second << Settings::Instance().delimery << abs(hexDelta[i].first) << '\n';
                        hexDelta[startPoint].first += hexDelta[i].first;
                        hexDelta[i].first = 0;
                    }
                    else
                    {
                        peopleRouting << outTime << Settings::Instance().delimery << hexDelta[startPoint].second << Settings::Instance().delimery <<
                            hexDelta[i].second << Settings::Instance().delimery << abs(hexDelta[startPoint].first) << '\n';
                        hexDelta[i].first += hexDelta[startPoint].first;
                        hexDelta[startPoint].first = 0;
                    }
                }

                if (hexDelta[startPoint].first > -1)
                {
                    startPoint++;
                    i = 0;
                }
                if (startPoint >= hexDelta.size())
                    break;
            }

            if ( i >= hexDelta.size())
                findRoute = true;
        }

        preview = iter;
    }
    std::cout << "Done People routing\n";
    peopleRouting.flush();
    peopleRouting.close();
}

size_t getRandValue(size_t a, size_t b)
{
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution < size_t > dis(a, b);

    return dis(gen);
}