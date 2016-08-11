var gulp = require('gulp');
var sass = require('gulp-sass');
var less = require('gulp-less');
var notify = require('gulp-notify');
var bower = require('gulp-bower');
var gf = require('gulp-filter');
var mbf = require('main-bower-files');
var debug = require('gulp-debug');

var conf = {
  sassPath: './static/sass',
  bowerDir: './bower_components'
};

gulp.task('bower.install', function () {
  return bower().pipe(gulp.dest(conf.bowerDir));
});

gulp.task('bower.copy', function () {
  var filter_js = gf('**/*.js', {restore: true});
  var filter_css = gf('**/*.css', {restore: true});
  var filter_less = gf('**/*.less', {restore: true});
  var filter_font = gf(['**/*.eot', '**/*.woff', '**/*.svg', '**/*.ttf'], {restore: true});

  return gulp.src(mbf({
      overrides: {
        bootstrap: {
          main: [
            './dist/js/bootstrap.js',
            './dist/css/*.min.*',
            './dist/fonts/*.*'
          ]
        }
      }
    }))

    .pipe(filter_js)
    .pipe(gulp.dest('./static/js'))
    .pipe(filter_js.restore)

    .pipe(filter_css)
    .pipe(gulp.dest('./static/css'))
    .pipe(filter_css.restore)

    .pipe(filter_less)
    .pipe(less())
    .pipe(gulp.dest('./static/css'))
    .pipe(filter_less.restore)

    .pipe(filter_font)
    .pipe(gulp.dest('./static/fonts'))
    .pipe(filter_font.restore)

    ;
});

gulp.task('bower', [
  'bower.install',
  'bower.copy'
]);

// Watch static/sass/style.scss,
// Compress all sass files into css
gulp.task('css', function () {
  return gulp.src(conf.sassPath + '/*.scss')
    .pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
    .pipe(gulp.dest('./static/css'));
});

gulp.task('watch', function () {
  gulp.watch(conf.sassPath + '/**/*.scss', ['css']);
});

gulp.task('default', ['bower', 'css']);
