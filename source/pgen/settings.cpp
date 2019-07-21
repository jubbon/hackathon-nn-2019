#include "settings.h"

#include <fstream>

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/prettywriter.h"

Settings & Settings::Instance()
{
    static Settings singleton;
    return singleton;
}

void Settings::readSetting()
{
    std::ifstream setting("settings.json");
    std::string settingStr((std::istreambuf_iterator<char>(setting)), {});

    rapidjson::Document settingDocument;
    settingDocument.Parse(settingStr.c_str());
    setting.close();

    if (!settingDocument.HasParseError())
    {
        for (auto itr = settingDocument.MemberBegin(); itr != settingDocument.MemberEnd(); ++itr)
        {
            if (itr->name.GetString() == std::string("settings"))
            {
                if (itr->value.IsObject())
                {
                    auto &value = itr->value;
                    if (value.HasMember("start_time"))
                        start_time = value["start_time"].GetUint();
                    if (value.HasMember("finish_time"))
                        finish_time = value["finish_time"].GetUint();
                    if (value.HasMember("interval"))
                        interval = value["interval"].GetUint();
                    if (value.HasMember("timeStr"))
                        timeStr = value["timeStr"].GetInt();
                    if (value.HasMember("publicTransportUsePercent"))
                        publicTransportUsePercent = value["publicTransportUsePercent"].GetDouble();
                    if (value.HasMember("delimery"))
                        delimery = *(value["delimery"].GetString());
                }
            }
        }
    }
}

Settings::Settings()
{
}

Settings::~Settings()
{
}
