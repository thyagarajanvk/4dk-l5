/* q3_b.c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "simlib.h"

#define SIM_END_TIME 100.0
#define ARRIVAL_RATE 100.0

/* packet sizes in bits from q2 description */
int PACKET_SIZES[] = {500, 1000, 1500, 2000, 2500};

typedef struct {
    int size_bits;
} Packet;

typedef struct {
    long max_tokens_Bt;        
    int max_data_Bd;           
    double token_gen_interval; 
    long current_tokens;       
    Fifoqueue_Ptr data_bucket;
    long total_packets_arrived;
    long packets_lost;
    long total_bits_sent;
} System_State;

void check_transmission(System_State *sys) {
    if (fifoqueue_size(sys->data_bucket) > 0) {
        Packet *pkt = (Packet *)fifoqueue_see_front(sys->data_bucket);
        
        /* check if we have enough tokens (bits) for this packet */
        if (sys->current_tokens >= pkt->size_bits) {
            sys->current_tokens -= pkt->size_bits;
            fifoqueue_get(sys->data_bucket);
            sys->total_bits_sent += pkt->size_bits;
            free(pkt);
            
            check_transmission(sys);
        }
    }
}

void event_token_gen(Simulation_Run_Ptr run, void *arg) {
    System_State *sys = (System_State *)simulation_run_data(run);
    double now = simulation_run_get_time(run);
    
    Event next_token;
    next_token.function = event_token_gen;
    next_token.attachment = NULL;
    next_token.description = "token_gen";
    simulation_run_schedule_event(run, next_token, now + sys->token_gen_interval);

    if (sys->current_tokens < sys->max_tokens_Bt) {
        sys->current_tokens++; 
    }
    check_transmission(sys);
}

void event_packet_arrival(Simulation_Run_Ptr run, void *arg) {
    System_State *sys = (System_State *)simulation_run_data(run);
    double now = simulation_run_get_time(run);
    
    Event next_arrival;
    next_arrival.function = event_packet_arrival;
    next_arrival.attachment = NULL;
    next_arrival.description = "arrival";
    simulation_run_schedule_event(run, next_arrival, now + exponential_generator(1.0 / ARRIVAL_RATE));

    sys->total_packets_arrived++;

    if (fifoqueue_size(sys->data_bucket) < sys->max_data_Bd) {
        Packet *new_pkt = (Packet *)malloc(sizeof(Packet));
        int r_idx = rand() % 5;
        new_pkt->size_bits = PACKET_SIZES[r_idx];

        fifoqueue_put(sys->data_bucket, (void *)new_pkt);
    } else {
        sys->packets_lost++;
    }
    check_transmission(sys);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        return 1;
    }
    long Bt = atol(argv[1]);
    int Bd = atoi(argv[2]);
    double rate = atof(argv[3]);
    int seed = atoi(argv[4]);

    Simulation_Run_Ptr run = simulation_run_new();
    random_generator_initialize(seed); 
    srand(seed);

    System_State sys;
    sys.max_tokens_Bt = Bt;
    sys.max_data_Bd = Bd;
    sys.token_gen_interval = 1.0 / rate;
    sys.current_tokens = 0;
    sys.data_bucket = fifoqueue_new();
    sys.total_packets_arrived = 0;
    sys.packets_lost = 0;
    sys.total_bits_sent = 0;

    simulation_run_set_data(run, &sys);

    Event evt;
    
    evt.function = event_packet_arrival;
    evt.attachment = NULL;
    evt.description = "first_arrival";
    simulation_run_schedule_event(run, evt, exponential_generator(1.0 / ARRIVAL_RATE));

    evt.function = event_token_gen;
    evt.attachment = NULL;
    evt.description = "first_token";
    simulation_run_schedule_event(run, evt, sys.token_gen_interval);

    while(simulation_run_get_time(run) < SIM_END_TIME) {
        simulation_run_execute_event(run);
    }

    double loss_rate = (double)sys.packets_lost / sys.total_packets_arrived;
    double output_bps = (double)sys.total_bits_sent / SIM_END_TIME;

    printf("%.5f,%.2f\n", loss_rate, output_bps);

    while(fifoqueue_size(sys.data_bucket) > 0) {
        free(fifoqueue_get(sys.data_bucket));
    }
    simulation_run_free_memory(run);
    return 0;
}