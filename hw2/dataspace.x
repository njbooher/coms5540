const MAX_TOPIC = 32;

struct ds_event_struct {
    string topic<MAX_TOPIC>;
    int value;
};

enum ds_publish_status {
    kError,
    kSuccess
};

typedef struct ds_event_struct ds_event_t;

typedef int ds_values_list<>;

program HW2Service {
    version ThisVersion {
            ds_publish_status publish(ds_event_t) = 1;
            ds_values_list retrieve(string) = 2;
    } = 1;
} = 0x23F6AE6C;