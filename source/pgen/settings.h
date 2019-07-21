#pragma once

//! Хранения настроек генераций данных
class Settings final
{
public:
    //! Конструктор копирования
    Settings(const Settings&) = delete;

    //! Оператор присваивания копированием (copy assignment)
    Settings& operator=(const Settings&) = delete;

    //! Конструктор перемещения
    Settings(Settings&& other) = delete;

    //! Оператор присваивания перемещением (move assignment)
    Settings& operator=(Settings&& other) = delete;

    //! Получить указатель
    static Settings & Instance();

    //! Чтение настроек приложения
    void readSetting();
public:
    //! время начала моделирования в минутах
    size_t start_time = 300;

    //! время окончания моделирования в минутах
    size_t finish_time = 1380;

    //! шаг моделирования
    size_t interval = 60;

    //! Разделитель для выходных csv файлов
    char delimery = ',';

    //! Вывод времени в виде строки
    bool timeStr = true;

    //! Процент людей, используемых общественный транспорт
    double publicTransportUsePercent = 0.4;

private:
    //! Конструктор
    Settings();

    //! Деструктор
    virtual ~Settings();
};