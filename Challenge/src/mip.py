import read_data as rd

class Vertex:
    def __init__(self, vertex_id, vertex_type, load, time_window=(0, float('inf'))):
        self.vertex_id = vertex_id
        self.vertex_type = vertex_type  # Can be "depot", "pickup", or "delivery"
        self.load = load
        self.time_window = time_window

    def __repr__(self):
        return f"Vertex(ID={self.vertex_id}, Type={self.vertex_type}, Load={self.load}, Time Window={self.time_window})"

class Arc:
    def __init__(self, start_vertex, end_vertex, travel_time):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.travel_time = travel_time

    def __repr__(self):
        return f"Arc({self.start_vertex} -> {self.end_vertex}, Time={self.travel_time})"


# Function to compute vertices from couriers and deliveries
def compute_vertices(couriers, deliveries):
    vertices = []
    Qmax = max(courier.capacity for courier in couriers)  # Max capacity across all couriers
    
    # Add depot vertices
    for courier in couriers:
        depot_vertex = Vertex(
            vertex_id=courier.location, 
            vertex_type="depot", 
            load=Qmax - courier.capacity  # Qsk := Qmax - Qk for depot vertices
        )
        vertices.append(depot_vertex)

    # Add pickup and delivery vertices
    for delivery in deliveries:
        pickup_vertex = Vertex(
            vertex_id=delivery.pickup_loc,
            vertex_type="pickup",
            load=delivery.capacity,
            time_window=(delivery.time_window_start, float('inf'))  # Time window for pickups
        )
        delivery_vertex = Vertex(
            vertex_id=delivery.dropoff_loc,
            vertex_type="delivery",
            load=-delivery.capacity,  # Negative load for delivery vertices
        )
        vertices.append(pickup_vertex)
        vertices.append(delivery_vertex)

    return vertices


# Function to compute arcs from travel time and vertices
def compute_arcs(couriers, deliveries, travel_time):
    arcs = []

    # Arc set A1: (Depot -> Pickup)
    for courier in couriers:
        for delivery in deliveries:
            arc = Arc(
                start_vertex=courier.location,  # Depot vertex id
                end_vertex=delivery.pickup_loc,  # Pickup vertex id
                travel_time=travel_time[courier.location - 1][delivery.pickup_loc - 1]  # Travel time between depot and pickup
            )
            arcs.append(arc)

    # Arc set A2: (Pickup -> Delivery)
    for i, delivery_1 in enumerate(deliveries):
        for j, delivery_2 in enumerate(deliveries):
            if i != j:  # Exclude arcs from a vertex to itself
                arc = Arc(
                    start_vertex=delivery_1.pickup_loc,
                    end_vertex=delivery_2.dropoff_loc,
                    travel_time=travel_time[delivery_1.pickup_loc - 1][delivery_2.dropoff_loc - 1]  # Travel time between pickups/deliveries
                )
                arcs.append(arc)

    # Arc set A3: (Delivery -> Depot)
    for delivery in deliveries:
        for courier in couriers:
            arc = Arc(
                start_vertex=delivery.dropoff_loc,
                end_vertex=courier.location,  # Depot vertex id
                travel_time=travel_time[delivery.dropoff_loc - 1][courier.location - 1]  # Travel time between delivery and depot
            )
            arcs.append(arc)

    # Arc set A4: (Depot -> Depot) - Loop at each depot
    for courier in couriers:
        arc = Arc(
            start_vertex=courier.location,
            end_vertex=courier.location,  # Loop back to itself
            travel_time=0  # No travel time for loops
        )
        arcs.append(arc)

    return arcs


# Example usage with the data loaded from CSV
def process_vertices_and_arcs(couriers, deliveries, travel_time):
    # Step 1: Compute the vertices
    vertices = compute_vertices(couriers, deliveries)
    print("Vertices:")
    for vertex in vertices:
        print(vertex)

    # Step 2: Compute the arcs
    arcs = compute_arcs(couriers, deliveries, travel_time)
    print("\nArcs:")
    for arc in arcs:
        print(arc)


# Main execution part
if __name__ == "__main__":
    # This is where you would load couriers, deliveries, and travel time from the CSV files as done in your existing code
    path = "Challenge/training_data/0b220d8f-ba16-4848-86ef-b446ef436fce"
    couriers, deliveries, travel_time = rd.process_instance_folder(path)  # Assuming you want the first instance

    process_vertices_and_arcs(couriers, deliveries, travel_time)

    import xpress as xp

    # Define the problem
    problem = xp.problem()

    # Data structures
    # K: set of vehicles
    # O: set of orders
    # V: set of vertices (S ∪ P ∪ D)
    # A: set of arcs (A1 ∪ A2 ∪ A3 ∪ A4)
    # T_uv: travel time between vertices u and v
    # Q_v: load at vertex v

    # Parameters (assuming you have these from your previous code or input data)
    # K: Set of vehicles (from couriers)
    K = [courier.courier_id for courier in couriers]

    # O: Set of orders (from deliveries)
    O = [delivery.delivery_id for delivery in deliveries]

    # V: Set of vertices (union of depot, pickup, and delivery vertices)
    # Depots are represented by courier locations, pickup and delivery vertices are the locations from deliveries
    depots = [courier.location for courier in couriers]  # Depot vertices (based on locations)
    pickups = [delivery.pickup_loc for delivery in deliveries]  # Pickup vertices (based on pickup locations)
    dropoffs = [delivery.dropoff_loc for delivery in deliveries]  # Delivery vertices (based on dropoff locations)

    V = list(set(depots + pickups + dropoffs))  # Union of depot, pickup, and delivery vertices, using `set` to avoid duplicates

    # A: Set of arcs
    # Arcs are the possible edges between depot, pickup, and delivery vertices
    A = []

    # A1: Depot -> Pickup
    for courier in couriers:
        for delivery in deliveries:
            A.append((courier.location, delivery.pickup_loc))

    # A2: Pickup -> Delivery and Pickup -> Pickup
    for delivery_1 in deliveries:
        for delivery_2 in deliveries:
            if delivery_1 != delivery_2:
                A.append((delivery_1.pickup_loc, delivery_2.dropoff_loc))
                A.append((delivery_1.pickup_loc, delivery_2.pickup_loc))

    # A3: Delivery -> Depot
    for delivery in deliveries:
        for courier in couriers:
            A.append((delivery.dropoff_loc, courier.location))

    # A4: Depot loops
    for courier in couriers:
        A.append((courier.location, courier.location))  # Loop at each depot

    # T: Travel times between vertices (2D list or dictionary based on travel_time matrix)
    T = {}
    for i, u in enumerate(V):
        for j, v in enumerate(V):
            T[(u, v)] = travel_time[i][j]  # Using the travel_time matrix from your loaded data

    # Q: Load values at each vertex
    Q = {}

    # Load at depot vertices: Qsk := Qmax - Qk
    Qmax = max(courier.capacity for courier in couriers)
    for courier in couriers:
        Q[courier.location] = Qmax - courier.capacity

    # Load at pickup vertices: Qpo = Qo (the capacity of the order)
    for delivery in deliveries:
        Q[delivery.pickup_loc] = delivery.capacity

    # Load at delivery vertices: Qdo = -Qo (the negative of the order capacity)
    for delivery in deliveries:
        Q[delivery.dropoff_loc] = -delivery.capacity

    # Maximum vehicle capacity Qmax is already computed as max(courier.capacity for courier in couriers)

    # Variables
    x = {(u, v, k): xp.var(vartype=xp.binary) for (u, v) in A for k in K}
    t = {v: xp.var(vartype=xp.continuous) for v in V}
    q = {v: xp.var(vartype=xp.continuous) for v in V}

    # Objective function: Minimize total time at delivery vertices
    problem.addObjective(xp.Sum(t[v] for v in V if v in D), sense=xp.minimize)

    # Constraints

    # 1. Flow conservation for all vertices: Sum of incoming arcs = sum of outgoing arcs
    for v in V:
        for k in K:
            problem.addConstraint(
                xp.Sum(x[u, v, k] for (u, v) in A if v == v) == xp.Sum(x[v, u, k] for (v, u) in A if v == v)
            )

    # 2. Each vehicle starts at its depot and leaves exactly once
    for k in K:
        problem.addConstraint(xp.Sum(x[sk, v, k] for (sk, v) in A if sk in S) == 1)

    # 3. Capacity constraints: Ensure vehicle capacity is not exceeded
    for (u, v, k) in A:
        problem.addConstraint(q[u] + (Q[v] + Qmax) * x[u, v, k] <= q[v] + Qmax)

    # 4. Time constraints for pickups and deliveries
    for (u, v, k) in A:
        problem.addConstraint(t[u] + (T[u, v] + T) * x[u, v, k] <= t[v] + T)

    # 5. Time window constraints for pickup and delivery vertices
    for v in V:
        if v in P or v in D:
            problem.addConstraint(l[v] <= t[v] <= u[v])  # Time window constraints

    # 6. Ensure that vehicles return to the depot after finishing deliveries
    for k in K:
        problem.addConstraint(xp.Sum(x[u, sk, k] for (u, sk) in A if sk in S) == 1)

    # 7. Binary constraint: Variables xuvk are binary
    for (u, v, k) in A:
        problem.addConstraint(x[u, v, k] in {0, 1})

    # Solve the problem
    problem.solve()

    # Extract the solution
    if problem.getSolution():
        for (u, v, k) in A:
            if xp.getSolution(x[u, v, k]) > 0.5:
                print(f"Vehicle {k} travels from {u} to {v}")

        for v in V:
            print(f"Time at vertex {v}: {xp.getSolution(t[v])}")
            print(f"Load at vertex {v}: {xp.getSolution(q[v])}")
    else:
        print("No feasible solution found.")