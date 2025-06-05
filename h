[1mdiff --git a/computer-security-Unsecured b/computer-security-Unsecured[m
[1m--- a/computer-security-Unsecured[m
[1m+++ b/computer-security-Unsecured[m
[36m@@ -1 +1 @@[m
[31m-Subproject commit 823213ab3a1ec80d0483a405f2a8310406ddcffc[m
[32m+[m[32mSubproject commit 823213ab3a1ec80d0483a405f2a8310406ddcffc-dirty[m
[1mdiff --git a/db.sqlite3 b/db.sqlite3[m
[1mindex d19f631..65ea089 100644[m
Binary files a/db.sqlite3 and b/db.sqlite3 differ
[1mdiff --git a/mainapp/templates/mainapp/reset_password.html b/mainapp/templates/mainapp/reset_password.html[m
[1mindex 5b48622..f731aaf 100644[m
[1m--- a/mainapp/templates/mainapp/reset_password.html[m
[1m+++ b/mainapp/templates/mainapp/reset_password.html[m
[36m@@ -11,6 +11,9 @@[m
 [m
 <form method="POST">[m
   {% csrf_token %}[m
[32m+[m[32m  {% if show_current_password %}[m
[32m+[m[32m    <input type="password" name="current_password" placeholder="Enter current password" required><br>[m
[32m+[m[32m  {% endif %}[m
   <input type="password" name="new_password1" placeholder="Enter new password" required><br>[m
   <input type="password" name="new_password2" placeholder="Confirm new password" required><br>[m
   <button type="submit">Reset Password</button>[m
[1mdiff --git a/mainapp/views.py b/mainapp/views.py[m
[1mindex e2195b4..286f72a 100644[m
[1m--- a/mainapp/views.py[m
[1m+++ b/mainapp/views.py[m
[36m@@ -205,12 +205,13 @@[m [mdef verify_reset_code(request):[m
         saved_code = request.session.get('reset_code', '')[m
 [m
         if entered_code == saved_code:[m
[31m-            return redirect('reset_password')[m
[32m+[m[32m            return redirect('reset_password')[m[41m  [m
         else:[m
[31m-            return render(request, 'mainapp/verify_reset_code.html', {'error': 'Invalid reset code.'})[m
[31m-[m
[31m-    return render(request, 'mainapp/verify_reset_code.html')[m
[32m+[m[32m            return render(request, 'mainapp/verify_reset_code.html', {[m
[32m+[m[32m                'error': 'Invalid reset code.'[m
[32m+[m[32m            })[m
 [m
[32m+[m[32m    return render(request, 'mainapp/verify_reset_code.html')[m[41m  [m
 def forgot_password(request):[m
     if request.method == 'POST':[m
         username = html.escape(request.POST.get('username', '').strip())[m
[36m@@ -277,7 +278,7 @@[m [mdef reset_password(request):[m
 [m
         return redirect('login')[m
 [m
[31m-    return render(request, 'mainapp/reset_password.html')[m
[32m+[m[32m    return render(request, 'mainapp/reset_password.html', {'show_current_password': False})[m
 [m
 def change_password(request):[m
     username = request.session.get('username', '')[m
[36m@@ -285,25 +286,45 @@[m [mdef change_password(request):[m
         return redirect('login')[m
 [m
     if request.method == 'POST':[m
[32m+[m[32m        current_password = request.POST.get('current_password', '')[m
         new_password1 = request.POST.get('new_password1', '')[m
         new_password2 = request.POST.get('new_password2', '')[m
 [m
[32m+[m[32m        try:[m
[32m+[m[32m            user = User.objects.get(username=username)[m
[32m+[m[32m        except User.DoesNotExist:[m
[32m+[m[32m            return render(request, 'mainapp/change_password.html', {[m
[32m+[m[32m                'error': 'User not found.'[m
[32m+[m[32m            })[m
[32m+[m
[32m+[m[32m        current_password_hash = hmac.new(user.salt, current_password.encode(), hashlib.sha256).hexdigest()[m
[32m+[m[32m        if current_password_hash != user.password_hash:[m
[32m+[m[32m            return render(request, 'mainapp/change_password.html', {[m
[32m+[m[32m                'error': 'Incorrect current password.'[m
[32m+[m[32m            })[m
[32m+[m
         if new_password1 != new_password2:[m
[31m-            return render(request, 'mainapp/reset_password.html', {'error': 'Passwords do not match.'})[m
[32m+[m[32m            return render(request, 'mainapp/change_password.html', {[m
[32m+[m[32m                'error': 'Passwords do not match.'[m
[32m+[m[32m            })[m
 [m
         is_valid, error_message = is_password_valid(new_password1)[m
         if not is_valid:[m
[31m-            return render(request, 'mainapp/reset_password.html', {'error': error_message})[m
[31m-[m
[31m-        try:[m
[31m-            user = User.objects.get(username=username)[m
[31m-        except User.DoesNotExist:[m
[31m-            return render(request, 'mainapp/reset_password.html', {'error': 'User not found.'})[m
[32m+[m[32m            return render(request, 'mainapp/change_password.html', {[m
[32m+[m[32m                'error': error_message[m
[32m+[m[32m            })[m
 [m
         new_password_hash_check = hmac.new(user.salt, new_password1.encode(), hashlib.sha256).hexdigest()[m
[31m-        previous_hashes = [user.password_hash, user.previous_password_hash1, user.previous_password_hash2, user.previous_password_hash3][m
[32m+[m[32m        previous_hashes = [[m
[32m+[m[32m            user.password_hash,[m
[32m+[m[32m            user.previous_password_hash1,[m
[32m+[m[32m            user.previous_password_hash2,[m
[32m+[m[32m            user.previous_password_hash3[m
[32m+[m[32m        ][m
         if new_password_hash_check in previous_hashes:[m
[31m-            return render(request, 'mainapp/reset_password.html', {'error': 'New password must be different from the last 3 passwords.'})[m
[32m+[m[32m            return render(request, 'mainapp/change_password.html', {[m
[32m+[m[32m                'error': 'New password must be different from the last 3 passwords.'[m
[32m+[m[32m            })[m
 [m
         user.previous_password_hash3 = user.previous_password_hash2[m
         user.previous_password_hash2 = user.previous_password_hash1[m
[36m@@ -318,7 +339,7 @@[m [mdef change_password(request):[m
 [m
         return redirect('home')[m
 [m
[31m-    return render(request, 'mainapp/reset_password.html')[m
[32m+[m[32m    return render(request, 'mainapp/change_password.html')[m
 [m
 def logout_user(request):[m
     request.session.flush()[m
