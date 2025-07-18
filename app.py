from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='.')

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'umrah.db')

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Create trips table
        c.execute('''CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            airline TEXT NOT NULL,
            airline_logo TEXT,
            hotel TEXT NOT NULL,  
            hotel_logo TEXT,    
            hotel_distance TEXT,  
            route TEXT NOT NULL,
            duration INTEGER NOT NULL,
            type TEXT NOT NULL,
            state TEXT NOT NULL,
            room5_price INTEGER NOT NULL,
            room5_status TEXT NOT NULL DEFAULT 'available',
            room4_price INTEGER NOT NULL,
            room4_status TEXT NOT NULL DEFAULT 'available',
            room3_price INTEGER NOT NULL,
            room3_status TEXT NOT NULL DEFAULT 'available',
            room2_price INTEGER NOT NULL,
            room2_status TEXT NOT NULL DEFAULT 'available'
        )''')

        # Create bookings table
        c.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            birth_place TEXT NOT NULL,
            passport_number TEXT NOT NULL,
            passport_issue_date TEXT NOT NULL,
            passport_expiry_date TEXT NOT NULL,
            umrah_type TEXT NOT NULL,
            room_type TEXT NOT NULL,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            booking_date TEXT NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips (id)
        )''')

        # Check if tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        logger.debug(f"Tables in database: {tables}")

        conn.commit()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

# Initialize database
init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/check-password', methods=['POST'])
def check_password():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        correct_password = "baya2288@."
        if data.get('password') == correct_password:
            return jsonify({'success': True})
        return jsonify({'success': False}), 401
    except Exception as e:
        logger.error(f"Password check error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard')
def serve_dashboard():
    return render_template('dashboard.html')

@app.route('/api/trips', methods=['GET'])
def get_all_trips():
    conn = None
    try:
        conn = get_db()
        c = conn.cursor()

        state_filter = request.args.get('state', 'all')
        type_filter = request.args.get('type', 'all')

        query = 'SELECT * FROM trips'
        params = []

        if state_filter != 'all':
            query += ' WHERE state = ?'
            params.append(state_filter)
            if type_filter != 'all':
                query += ' AND type = ?'
                params.append(type_filter)
        elif type_filter != 'all':
            query += ' WHERE type = ?'
            params.append(type_filter)

        logger.debug(f"Executing query: {query} with params: {params}")
        c.execute(query, params)
        trips = c.fetchall()

        trips_list = []
        for trip in trips:
            trip_data = {
                'id': trip['id'],
                'date': trip['date'],
                'airline': trip['airline'],
                'airline_logo': trip['airline_logo'] or '',
                'hotel': trip['hotel'],
                'hotel_logo': trip['hotel_logo'] or '',
                'hotel_distance': trip['hotel_distance'] or '',
                'route': trip['route'],
                'duration': trip['duration'],
                'type': trip['type'],
                'state': trip['state'],
                'room5': {
                    'price': trip['room5_price'],
                    'status': trip['room5_status']
                },
                'room4': {
                    'price': trip['room4_price'],
                    'status': trip['room4_status']
                },
                'room3': {
                    'price': trip['room3_price'],
                    'status': trip['room3_status']
                },
                'room2': {
                    'price': trip['room2_price'],
                    'status': trip['room2_status']
                }
            }
            trips_list.append(trip_data)

        return jsonify({'trips': trips_list})
    except Exception as e:
        logger.error(f"Error getting trips: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    conn = None
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
        trip = c.fetchone()

        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        trip_data = {
            'id': trip['id'],
            'date': trip['date'],
            'airline': trip['airline'],
            'airline_logo': trip['airline_logo'] or '',
            'hotel': trip['hotel'],
            'hotel_logo': trip['hotel_logo'] or '',
            'hotel_distance': trip['hotel_distance'] or '',
            'route': trip['route'],
            'duration': trip['duration'],
            'type': trip['type'],
            'state': trip['state'],
            'room5': {
                'price': trip['room5_price'],
                'status': trip['room5_status']
            },
            'room4': {
                'price': trip['room4_price'],
                'status': trip['room4_status']
            },
            'room3': {
                'price': trip['room3_price'],
                'status': trip['room3_status']
            },
            'room2': {
                'price': trip['room2_price'],
                'status': trip['room2_status']
            }
        }

        return jsonify(trip_data)
    except Exception as e:
        logger.error(f"Error getting trip {trip_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/trips', methods=['POST'])
def create_trip():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = [
            'date', 'airline', 'hotel', 'route', 'duration', 'type', 'state',
            'room5_price', 'room4_price', 'room3_price', 'room2_price'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db()
        c = conn.cursor()

        c.execute('''INSERT INTO trips 
            (date, airline, airline_logo, hotel, hotel_logo, hotel_distance, route, duration, type, state,
             room5_price, room5_status, room4_price, room4_status,
             room3_price, room3_status, room2_price, room2_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (
                      data['date'], 
                      data['airline'], 
                      data.get('airline_logo', ''),
                      data['hotel'], 
                      data.get('hotel_logo', ''), 
                      data.get('hotel_distance', ''),
                      data['route'], 
                      data['duration'], 
                      data['type'], 
                      data['state'],
                      data['room5_price'], 
                      'available', 
                      data['room4_price'], 
                      'available',
                      data['room3_price'], 
                      'available', 
                      data['room2_price'], 
                      'available'
                  ))

        trip_id = c.lastrowid
        conn.commit()

        return jsonify({
            'message': 'Trip created successfully',
            'id': trip_id,
            'trip': {
                'id': trip_id,
                **data
            }
        }), 201
    except Exception as e:
        logger.error(f"Error creating trip: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
        trip = c.fetchone()

        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        update_fields = {
            'date': data.get('date', trip['date']),
            'airline': data.get('airline', trip['airline']),
            'airline_logo': data.get('airline_logo', trip['airline_logo']),
            'hotel': data.get('hotel', trip['hotel']),
            'hotel_logo': data.get('hotel_logo', trip['hotel_logo']),
            'hotel_distance': data.get('hotel_distance', trip['hotel_distance']),
            'route': data.get('route', trip['route']),
            'duration': data.get('duration', trip['duration']),
            'type': data.get('type', trip['type']),
            'state': data.get('state', trip['state']),
            'room5_price': data.get('room5_price', trip['room5_price']),
            'room4_price': data.get('room4_price', trip['room4_price']),
            'room3_price': data.get('room3_price', trip['room3_price']),
            'room2_price': data.get('room2_price', trip['room2_price'])
        }

        c.execute('''UPDATE trips SET 
                        date = ?, airline = ?, airline_logo = ?, hotel = ?, hotel_logo = ?, 
                        hotel_distance = ?, route = ?, duration = ?, type = ?, state = ?, 
                        room5_price = ?, room4_price = ?, room3_price = ?, room2_price = ?
                     WHERE id = ?''',
                  (
                      update_fields['date'], 
                      update_fields['airline'], 
                      update_fields['airline_logo'],
                      update_fields['hotel'], 
                      update_fields['hotel_logo'], 
                      update_fields['hotel_distance'],
                      update_fields['route'], 
                      update_fields['duration'], 
                      update_fields['type'], 
                      update_fields['state'],
                      update_fields['room5_price'], 
                      update_fields['room4_price'],
                      update_fields['room3_price'], 
                      update_fields['room2_price'], 
                      trip_id
                  ))

        conn.commit()
        return jsonify({
            'message': 'Trip updated successfully',
            'trip': {
                'id': trip_id,
                **update_fields
            }
        })
    except Exception as e:
        logger.error(f"Error updating trip {trip_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/trips/<int:trip_id>/status', methods=['PUT'])
def update_trip_status(trip_id):
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['room5_status', 'room4_status', 'room3_status', 'room2_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
        trip = c.fetchone()

        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        c.execute('''UPDATE trips SET 
            room5_status = ?, room4_status = ?, room3_status = ?, room2_status = ?
            WHERE id = ?''',
                  (
                      data['room5_status'], 
                      data['room4_status'],
                      data['room3_status'], 
                      data['room2_status'], 
                      trip_id
                  ))

        conn.commit()
        return jsonify({'message': 'Trip status updated successfully'})
    except Exception as e:
        logger.error(f"Error updating trip {trip_id} status: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = [
            'tripId', 'firstName', 'lastName', 'email', 'phone',
            'birthDate', 'birthPlace', 'passportNumber',
            'passportIssueDate', 'passportExpiryDate',
            'umrahType', 'roomType'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db()
        c = conn.cursor()

        # Check if trip exists
        c.execute('SELECT * FROM trips WHERE id = ?', (data['tripId'],))
        trip = c.fetchone()

        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        # Check room availability
        room_status_field = f'room{data["roomType"]}_status'
        if trip[room_status_field] == 'full':
            return jsonify({'error': 'This room type is fully booked'}), 400

        # Insert booking
        c.execute('''INSERT INTO bookings 
            (trip_id, first_name, last_name, email, phone, birth_date, birth_place,
             passport_number, passport_issue_date, passport_expiry_date, umrah_type,
             room_type, notes, booking_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (
                      data['tripId'], 
                      data['firstName'], 
                      data['lastName'], 
                      data['email'],
                      data['phone'], 
                      data['birthDate'], 
                      data['birthPlace'], 
                      data['passportNumber'],
                      data['passportIssueDate'], 
                      data['passportExpiryDate'], 
                      data['umrahType'],
                      data['roomType'], 
                      data.get('notes', ''), 
                      datetime.now().isoformat()
                  ))

        booking_id = c.lastrowid
        conn.commit()

        return jsonify({
            'message': 'Booking created successfully',
            'id': booking_id
        }), 201
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if 'status' not in data:
            return jsonify({'error': 'Missing required field: status'}), 400

        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        booking = c.fetchone()

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        c.execute('UPDATE bookings SET status = ? WHERE id = ?',
                  (data['status'], booking_id))

        conn.commit()
        return jsonify({'message': 'Booking status updated successfully'})
    except Exception as e:
        logger.error(f"Error updating booking {booking_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = None
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        booking = c.fetchone()

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        c.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        conn.commit()

        return jsonify({'message': 'Booking deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting booking {booking_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = None
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT COUNT(*) FROM bookings')
        total_bookings = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM bookings WHERE status = ?', ('pending',))
        pending_bookings = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM bookings WHERE status = ?', ('approved',))
        approved_bookings = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM trips')
        total_trips = c.fetchone()[0]

        # Get bookings by state
        c.execute('''SELECT b.birth_place as state, COUNT(*) as count 
                   FROM bookings b GROUP BY b.birth_place''')
        state_stats = {row['state']: row['count'] for row in c.fetchall()}

        # Get bookings by type
        c.execute('''SELECT umrah_type as type, COUNT(*) as count 
                   FROM bookings GROUP BY umrah_type''')
        type_stats = {row['type']: row['count'] for row in c.fetchall()}

        return jsonify({
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'approved_bookings': approved_bookings,
            'total_trips': total_trips,
            'state_stats': state_stats,
            'type_stats': type_stats
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    conn = None
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('''SELECT b.*, t.date as trip_date, t.airline as trip_airline 
                   FROM bookings b JOIN trips t ON b.trip_id = t.id''')
        bookings = c.fetchall()

        bookings_list = []
        for booking in bookings:
            bookings_list.append({
                'id': booking['id'],
                'tripId': booking['trip_id'],
                'firstName': booking['first_name'],
                'lastName': booking['last_name'],
                'email': booking['email'],
                'phone': booking['phone'],
                'birthDate': booking['birth_date'],
                'birthPlace': booking['birth_place'],
                'passportNumber': booking['passport_number'],
                'passportIssueDate': booking['passport_issue_date'],
                'passportExpiryDate': booking['passport_expiry_date'],
                'umrahType': booking['umrah_type'],
                'roomType': booking['room_type'],
                'notes': booking['notes'],
                'status': booking['status'],
                'bookingDate': booking['booking_date'],
                'trip': {
                    'date': booking['trip_date'],
                    'airline': booking['trip_airline']
                }
            })

        return jsonify(bookings_list)  # تم تغيير هذا السطر ليعيد المصفوفة مباشرة
    except Exception as e:
        logger.error(f"Error getting bookings: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()            

@app.route('/api/add-test-data', methods=['GET'])
def add_test_data():
    conn = None
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Add sample trip
        c.execute('''INSERT INTO trips 
            (date, airline, airline_logo, hotel, hotel_logo, hotel_distance, 
             route, duration, type, state,
             room5_price, room4_price, room3_price, room2_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                '2023-12-01', 
                'الجزائرية', 
                'airline_algerie.png',
                'الأنوار', 
                'anwar.png',
                '300م',
                'الجزائر-جدة-مكة', 
                10, 
                'economy', 
                'algiers',
                50000, 
                60000, 
                70000, 
                80000
            ))
        
        # Add sample booking
        c.execute('''INSERT INTO bookings 
            (trip_id, first_name, last_name, email, phone, birth_date, birth_place,
             passport_number, passport_issue_date, passport_expiry_date, umrah_type,
             room_type, notes, booking_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                1,
                'محمد',
                'أحمد',
                'mohamed@example.com',
                '0551234567',
                '1990-01-01',
                'algiers',
                '12345678',
                '2020-01-01',
                '2025-01-01',
                'single',
                '2',
                'ملاحظات اختبارية',
                datetime.now().isoformat()
            ))
        
        conn.commit()
        return jsonify({'message': 'تمت إضافة بيانات الاختبار بنجاح'})
    except Exception as e:
        logger.error(f"Error adding test data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
